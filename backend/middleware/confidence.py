"""
Confidence Scoring System for Data Sources

Tracks confidence scores, data quality metrics, and source attribution
for all agent outputs.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class EvidenceStrength(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class DataSource(BaseModel):
    name: str
    weight: float  # 0.0 to 1.0
    records_found: int
    last_updated: Optional[datetime] = None
    reliability_score: float = 0.8  # Historical reliability


class DataQuality(BaseModel):
    completeness: float  # 0.0 to 1.0 - how complete is the data
    recency: float  # 0.0 to 1.0 - how recent is the data
    source_reliability: float  # 0.0 to 1.0 - how reliable is the source
    consistency: float = 1.0  # 0.0 to 1.0 - consistency across sources


class ConfidenceScore(BaseModel):
    agent: str
    confidence: float  # 0.0 to 1.0
    data_quality: DataQuality
    evidence_strength: EvidenceStrength
    sources: List[DataSource]
    reasoning: str
    timestamp: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "confidence": round(self.confidence, 3),
            "data_quality": {
                "completeness": round(self.data_quality.completeness, 3),
                "recency": round(self.data_quality.recency, 3),
                "source_reliability": round(self.data_quality.source_reliability, 3),
                "consistency": round(self.data_quality.consistency, 3),
            },
            "evidence_strength": self.evidence_strength.value,
            "sources": [
                {
                    "name": s.name,
                    "weight": round(s.weight, 3),
                    "records": s.records_found,
                    "reliability": round(s.reliability_score, 3)
                }
                for s in self.sources
            ],
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat()
        }


class ConfidenceCalculator:
    """
    Calculate confidence scores based on multiple factors
    """
    
    @staticmethod
    def calculate_clinical_trials_confidence(
        trials_found: int,
        phase_distribution: Dict[str, int],
        data_recency_days: int
    ) -> ConfidenceScore:
        """
        Calculate confidence for clinical trials data
        """
        # Base confidence on number of trials
        if trials_found == 0:
            base_confidence = 0.0
        elif trials_found < 3:
            base_confidence = 0.4
        elif trials_found < 10:
            base_confidence = 0.6
        elif trials_found < 20:
            base_confidence = 0.8
        else:
            base_confidence = 0.9
        
        # Adjust for phase distribution (Phase 3/4 more reliable)
        phase_3_4 = phase_distribution.get("Phase 3", 0) + phase_distribution.get("Phase 4", 0)
        if phase_3_4 > 0:
            base_confidence += 0.1
        
        # Adjust for recency
        if data_recency_days < 365:
            recency_score = 1.0
        elif data_recency_days < 730:
            recency_score = 0.8
        elif data_recency_days < 1825:
            recency_score = 0.6
        else:
            recency_score = 0.4
        
        # Calculate completeness
        completeness = min(trials_found / 20, 1.0)
        
        # Determine evidence strength
        if trials_found >= 10 and phase_3_4 >= 3:
            evidence = EvidenceStrength.HIGH
        elif trials_found >= 5:
            evidence = EvidenceStrength.MEDIUM
        elif trials_found >= 1:
            evidence = EvidenceStrength.LOW
        else:
            evidence = EvidenceStrength.INSUFFICIENT
        
        final_confidence = min(base_confidence * recency_score, 1.0)
        
        return ConfidenceScore(
            agent="clinical_trials",
            confidence=final_confidence,
            data_quality=DataQuality(
                completeness=completeness,
                recency=recency_score,
                source_reliability=0.9,  # ClinicalTrials.gov is highly reliable
                consistency=1.0
            ),
            evidence_strength=evidence,
            sources=[
                DataSource(
                    name="ClinicalTrials.gov",
                    weight=1.0,
                    records_found=trials_found,
                    reliability_score=0.9
                )
            ],
            reasoning=f"Found {trials_found} trials. Phase 3/4: {phase_3_4}. Data recency: {data_recency_days} days."
        )
    
    @staticmethod
    def calculate_patent_confidence(
        patents_found: int,
        active_patents: int,
        fto_risk_level: str
    ) -> ConfidenceScore:
        """
        Calculate confidence for patent analysis
        """
        if patents_found == 0:
            base_confidence = 0.3  # Low confidence but not zero
        elif patents_found < 5:
            base_confidence = 0.6
        elif patents_found < 20:
            base_confidence = 0.8
        else:
            base_confidence = 0.9
        
        # Adjust for FTO risk
        risk_multipliers = {
            "low": 1.0,
            "medium": 0.9,
            "high": 0.7
        }
        base_confidence *= risk_multipliers.get(fto_risk_level.lower(), 0.8)
        
        completeness = min(patents_found / 30, 1.0)
        
        evidence = EvidenceStrength.HIGH if patents_found >= 10 else EvidenceStrength.MEDIUM
        
        return ConfidenceScore(
            agent="patents",
            confidence=base_confidence,
            data_quality=DataQuality(
                completeness=completeness,
                recency=0.95,  # Patent data is usually current
                source_reliability=0.95,  # USPTO/patent databases are authoritative
                consistency=1.0
            ),
            evidence_strength=evidence,
            sources=[
                DataSource(
                    name="Patent Database",
                    weight=1.0,
                    records_found=patents_found,
                    reliability_score=0.95
                )
            ],
            reasoning=f"Found {patents_found} patents ({active_patents} active). FTO risk: {fto_risk_level}."
        )
    
    @staticmethod
    def calculate_rag_confidence(
        documents_found: int,
        avg_similarity_score: float,
        top_score: float
    ) -> ConfidenceScore:
        """
        Calculate confidence for RAG/internal documents
        """
        if documents_found == 0:
            base_confidence = 0.0
        elif top_score < 0.5:
            base_confidence = 0.3
        elif top_score < 0.7:
            base_confidence = 0.6
        elif top_score < 0.85:
            base_confidence = 0.8
        else:
            base_confidence = 0.95
        
        completeness = min(documents_found / 10, 1.0)
        
        evidence = (
            EvidenceStrength.HIGH if top_score >= 0.85
            else EvidenceStrength.MEDIUM if top_score >= 0.7
            else EvidenceStrength.LOW
        )
        
        return ConfidenceScore(
            agent="internal_insights",
            confidence=base_confidence,
            data_quality=DataQuality(
                completeness=completeness,
                recency=0.9,  # Internal docs are usually recent
                source_reliability=0.95,  # Internal data is highly reliable
                consistency=avg_similarity_score
            ),
            evidence_strength=evidence,
            sources=[
                DataSource(
                    name="Internal Clinical Reports",
                    weight=1.0,
                    records_found=documents_found,
                    reliability_score=0.95
                )
            ],
            reasoning=f"Found {documents_found} relevant documents. Top similarity: {top_score:.3f}, Avg: {avg_similarity_score:.3f}."
        )
    
    @staticmethod
    def calculate_drug_analysis_confidence(
        passes_lipinski: bool,
        admet_available: bool,
        molecular_weight: float
    ) -> ConfidenceScore:
        """
        Calculate confidence for drug molecular analysis
        """
        base_confidence = 0.95  # Molecular calculations are deterministic
        
        if not passes_lipinski:
            base_confidence -= 0.1
        
        if not admet_available:
            base_confidence -= 0.15
        
        evidence = EvidenceStrength.HIGH
        
        return ConfidenceScore(
            agent="drug_analysis",
            confidence=base_confidence,
            data_quality=DataQuality(
                completeness=1.0 if admet_available else 0.7,
                recency=1.0,  # Calculations are current
                source_reliability=0.98,  # RDKit is highly reliable
                consistency=1.0
            ),
            evidence_strength=evidence,
            sources=[
                DataSource(
                    name="RDKit Molecular Analysis",
                    weight=1.0,
                    records_found=1,
                    reliability_score=0.98
                )
            ],
            reasoning=f"Lipinski: {passes_lipinski}, ADMET: {admet_available}, MW: {molecular_weight:.1f}"
        )
    
    @staticmethod
    def aggregate_confidence_scores(scores: List[ConfidenceScore]) -> Dict[str, Any]:
        """
        Aggregate multiple confidence scores into overall assessment
        """
        if not scores:
            return {
                "overall_confidence": 0.0,
                "evidence_strength": "insufficient",
                "agent_scores": []
            }
        
        # Weighted average (can adjust weights based on agent importance)
        weights = {
            "clinical_trials": 0.3,
            "patents": 0.2,
            "internal_insights": 0.25,
            "drug_analysis": 0.15,
            "web_intel": 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for score in scores:
            weight = weights.get(score.agent, 0.1)
            weighted_sum += score.confidence * weight
            total_weight += weight
        
        overall_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Determine overall evidence strength
        high_count = sum(1 for s in scores if s.evidence_strength == EvidenceStrength.HIGH)
        medium_count = sum(1 for s in scores if s.evidence_strength == EvidenceStrength.MEDIUM)
        
        if high_count >= 2:
            overall_evidence = "high"
        elif high_count >= 1 or medium_count >= 2:
            overall_evidence = "medium"
        elif medium_count >= 1:
            overall_evidence = "low"
        else:
            overall_evidence = "insufficient"
        
        return {
            "overall_confidence": round(overall_confidence, 3),
            "evidence_strength": overall_evidence,
            "agent_scores": [score.to_dict() for score in scores],
            "total_sources": sum(len(score.sources) for score in scores),
            "timestamp": datetime.utcnow().isoformat()
        }
