from typing import Dict, Any
import json
from utils.llm_utils import get_llm
from config import GUIDELINES_JSON
from tools.internal_rag_tool import search_internal_docs, format_results_as_context


class InternalInsightsAgent:
    """
    Analyzes internal clinical experiment reports (via RAG) and
    regulatory guidelines to produce strategic insights.
    """

    def __init__(self):
        self.llm = get_llm()

    async def analyze_guidelines(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Combine RAG over internal PDFs with structured guidelines analysis"""
        query = state.get("query", "")
        molecule = state.get("molecule", "")

        # 1. Retrieve relevant passages from internal experiment reports
        rag_context = self._retrieve_internal_context(query, molecule)

        # 2. Load structured regulatory guidelines
        guidelines_data = self._load_guidelines(query, molecule)

        # 3. Generate combined insights
        insights = await self._generate_insights(
            guidelines_data, rag_context, query, molecule
        )

        state["guidelines_data"] = guidelines_data
        state["internal_rag_context"] = rag_context
        state["regulatory_insights"] = insights

        return state

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _retrieve_internal_context(self, query: str, molecule: str) -> str:
        """Search the FAISS index for relevant internal report passages"""
        search_query = f"{molecule} {query}".strip()
        result = search_internal_docs({"query": search_query, "k": 5})

        if result.get("error"):
            # Vector store not yet built or unavailable — degrade gracefully
            return f"Internal document search unavailable: {result['error']}"

        return format_results_as_context(result.get("results", []))

    def _load_guidelines(self, query: str, molecule: str) -> Dict:
        """Load and filter structured regulatory guidelines"""
        try:
            with open(GUIDELINES_JSON, "r") as f:
                data = json.load(f)
            return self._filter_guidelines(data, query, molecule)
        except FileNotFoundError:
            return {}

    def _filter_guidelines(self, data: Dict, query: str, molecule: str) -> Dict:
        """Keep only guideline entries relevant to the query/molecule"""
        relevant = {}
        for category, guidelines in data.items():
            if isinstance(guidelines, list):
                filtered = [
                    g for g in guidelines
                    if (molecule and molecule.lower() in str(g).lower())
                    or (query and query.lower() in str(g).lower())
                ]
                if filtered:
                    relevant[category] = filtered
            elif isinstance(guidelines, dict):
                relevant[category] = guidelines
        return relevant

    async def _generate_insights(
        self,
        guidelines: Dict,
        rag_context: str,
        query: str,
        molecule: str,
    ) -> str:
        """Generate regulatory and strategic insights using both data sources"""

        guidelines_text = (
            json.dumps(guidelines, indent=2) if guidelines
            else "No structured guidelines matched this query."
        )

        prompt = f"""
You are a pharmaceutical regulatory strategist.

Analyze the following information and generate strategic insights for a drug repurposing opportunity.

## Query
{query}

## Molecule
{molecule or "Not specified"}

## Internal Clinical Experiment Findings (from internal reports)
{rag_context}

## Regulatory Guidelines
{guidelines_text}

Provide a structured analysis covering:
1. Key findings from internal experiments relevant to this repurposing opportunity
2. Regulatory pathway recommendations (e.g., 505(b)(2), orphan drug, breakthrough therapy)
3. Critical approval requirements and data gaps
4. Potential regulatory risks and mitigation strategies
5. Strategic timeline estimates

Be specific and actionable. Reference internal findings where relevant.
"""

        response = await self.llm.ainvoke(prompt)
        return response.content
