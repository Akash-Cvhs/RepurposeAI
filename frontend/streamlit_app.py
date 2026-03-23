import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="VHS Drug Repurposing Platform",
    page_icon="💊",
    layout="wide"
)

def main():
    st.title("💊 VHS Drug Repurposing Platform")
    st.markdown("AI-powered drug repurposing analysis with multi-agent intelligence")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Choose a page", ["New Analysis", "Analysis History", "About"])
    
    if page == "New Analysis":
        show_analysis_page()
    elif page == "Analysis History":
        show_history_page()
    else:
        show_about_page()

def show_analysis_page():
    st.header("🔬 New Drug Repurposing Analysis")
    
    # Input form
    with st.form("analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            query = st.text_area(
                "Research Query",
                placeholder="e.g., 'Alzheimer's disease treatment options' or 'COVID-19 therapeutics'",
                height=100
            )
        
        with col2:
            molecule = st.text_input(
                "Molecule/Drug (Optional)",
                placeholder="e.g., 'aspirin', 'metformin', 'hydroxychloroquine'"
            )
        
        submitted = st.form_submit_button("🚀 Run Analysis", type="primary")
    
    if submitted and query:
        run_analysis(query, molecule)
    elif submitted:
        st.error("Please enter a research query")

def run_analysis(query: str, molecule: str = None):
    """Execute drug repurposing analysis"""
    
    with st.spinner("🤖 Running multi-agent analysis..."):
        try:
            # Prepare request
            payload = {"query": query}
            if molecule:
                payload["molecule"] = molecule
            
            # Call backend API
            response = requests.post(f"{BACKEND_URL}/run", json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Analysis completed! Run ID: {result['run_id']}")
                
                # Display results
                if result.get("report_path"):
                    st.info(f"📄 Report saved to: {result['report_path']}")
                    
                    # Offer download (if accessible)
                    if os.path.exists(result["report_path"]):
                        with open(result["report_path"], "rb") as f:
                            st.download_button(
                                "📥 Download Report",
                                f.read(),
                                file_name=f"drug_repurposing_report_{result['run_id']}.pdf",
                                mime="application/pdf"
                            )
            else:
                st.error(f"❌ Analysis failed: {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("⏰ Analysis timed out. Please try again with a simpler query.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend. Please ensure the backend server is running.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

def show_history_page():
    st.header("📚 Analysis History")
    
    try:
        # Fetch run history
        response = requests.get(f"{BACKEND_URL}/archives")
        
        if response.status_code == 200:
            runs = response.json()
            
            if runs:
                st.write(f"Found {len(runs)} previous analyses:")
                
                # Display runs in a table
                for run in reversed(runs[-10:]):  # Show last 10 runs
                    with st.expander(f"🔬 {run['query'][:50]}... - {run['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Query:** {run['query']}")
                            if run.get('molecule'):
                                st.write(f"**Molecule:** {run['molecule']}")
                            st.write(f"**Status:** {run['status']}")
                        
                        with col2:
                            st.write(f"**Run ID:** {run['id']}")
                            st.write(f"**Timestamp:** {run['timestamp']}")
                            if run.get('report_path') and os.path.exists(run['report_path']):
                                with open(run['report_path'], "rb") as f:
                                    st.download_button(
                                        "📥 Download Report",
                                        f.read(),
                                        file_name=f"report_{run['id']}.pdf",
                                        mime="application/pdf",
                                        key=run['id']
                                    )
            else:
                st.info("No previous analyses found. Run your first analysis!")
                
        else:
            st.error("Failed to fetch analysis history")
            
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to backend. Please ensure the backend server is running.")
    except Exception as e:
        st.error(f"❌ Error fetching history: {str(e)}")

def show_about_page():
    st.header("ℹ️ About VHS Drug Repurposing Platform")
    
    st.markdown("""
    ### 🎯 Purpose
    This platform leverages AI agents to analyze drug repurposing opportunities by integrating multiple data sources:
    
    - **Clinical Trials Data** - Efficacy and safety signals
    - **Patent Landscape** - Freedom-to-operate assessment  
    - **Regulatory Guidelines** - Approval pathway insights
    - **Market Intelligence** - Commercial viability analysis
    
    ### 🤖 Multi-Agent Architecture
    - **Master Agent** - Orchestrates the analysis workflow
    - **Clinical Trials Agent** - Analyzes trial data and outcomes
    - **Patent Agent** - Assesses IP landscape and FTO risks
    - **Internal Insights Agent** - Reviews regulatory guidelines
    - **Web Intelligence Agent** - Gathers market intelligence
    - **Report Generator Agent** - Compiles comprehensive reports
    
    ### 🛠️ Technology Stack
    - **Backend:** FastAPI + LangGraph + LangChain
    - **Frontend:** Streamlit
    - **AI Models:** OpenAI GPT-4 / Anthropic Claude
    - **Data Processing:** Pandas, ReportLab
    
    ### 📊 Sample Queries
    Try these example queries:
    - "Alzheimer's disease treatment with existing cardiovascular drugs"
    - "COVID-19 therapeutics from approved anti-inflammatory medications"
    - "Cancer immunotherapy using repurposed psychiatric medications"
    
    ### 🔧 Setup Instructions
    1. Start the backend: `cd backend && uvicorn app:app --reload`
    2. Start the frontend: `cd frontend && streamlit run streamlit_app.py`
    3. Configure your API keys in `.env` file
    """)

if __name__ == "__main__":
    main()