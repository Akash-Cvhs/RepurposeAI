# Data Sources & Schema Definitions

## Overview
This document defines the data schemas and sources used by the VHS Drug Repurposing Platform for clinical trials, patents, regulatory guidelines, and market intelligence.

## Clinical Trials Data

### Schema: trials.csv
```csv
nct_id,title,condition,intervention,phase,status,sponsor,enrollment
```

#### Field Definitions
- **nct_id**: ClinicalTrials.gov identifier (e.g., NCT12345678)
- **title**: Full study title
- **condition**: Primary medical condition being studied
- **intervention**: Drug/treatment being tested
- **phase**: Clinical trial phase (Phase 1, Phase 2, Phase 3, Phase 4)
- **status**: Current study status (Recruiting, Active, Completed, Terminated)
- **sponsor**: Organization conducting the study
- **enrollment**: Target or actual number of participants

#### Data Sources
- **Primary**: ClinicalTrials.gov API
- **Secondary**: EudraCT (European trials)
- **Tertiary**: WHO ICTRP (International registry)

#### Sample Query Patterns
```python
# Filter by condition
trials_df[trials_df['condition'].str.contains('Alzheimer', case=False)]

# Filter by intervention
trials_df[trials_df['intervention'].str.contains('aspirin', case=False)]

# Filter by phase and status
trials_df[(trials_df['phase'] == 'Phase 3') & (trials_df['status'] == 'Completed')]
```

## Patent Data

### Schema: patents.csv
```csv
patent_number,title,assignee,filing_date,expiration_date,abstract,status
```

#### Field Definitions
- **patent_number**: Official patent identifier (e.g., US10123456)
- **title**: Patent title
- **assignee**: Patent holder/owner organization
- **filing_date**: Date patent application was filed (YYYY-MM-DD)
- **expiration_date**: Date patent expires (YYYY-MM-DD)
- **abstract**: Brief description of the invention
- **status**: Patent status (Active, Expired, Pending, Abandoned)

#### Data Sources
- **Primary**: USPTO API (US patents)
- **Secondary**: EPO API (European patents)
- **Tertiary**: Google Patents API (global search)

#### FTO Analysis Patterns
```python
# Check for active patents
active_patents = patents_df[patents_df['status'] == 'Active']

# Find patents expiring soon
import pandas as pd
from datetime import datetime, timedelta

soon_expiring = patents_df[
    pd.to_datetime(patents_df['expiration_date']) < 
    datetime.now() + timedelta(years=2)
]

# Search by molecule/compound
molecule_patents = patents_df[
    patents_df['title'].str.contains(molecule, case=False) |
    patents_df['abstract'].str.contains(molecule, case=False)
]
```

## Regulatory Guidelines

### Schema: guidelines.json
```json
{
  "fda_guidance": {
    "drug_repurposing": [...],
    "rare_diseases": [...]
  },
  "ema_guidance": {
    "repurposing": [...]
  },
  "ich_guidelines": {
    "safety": [...],
    "efficacy": [...]
  },
  "therapeutic_areas": {
    "oncology": {
      "endpoints": [...],
      "biomarkers": [...],
      "considerations": [...]
    }
  }
}
```

#### Structure Definitions
- **fda_guidance**: FDA-specific regulatory pathways and requirements
- **ema_guidance**: European Medicines Agency guidelines
- **ich_guidelines**: International Council for Harmonisation standards
- **therapeutic_areas**: Disease-specific regulatory considerations

#### Usage Patterns
```python
import json

# Load guidelines
with open('guidelines.json', 'r') as f:
    guidelines = json.load(f)

# Get FDA repurposing guidance
fda_repurposing = guidelines['fda_guidance']['drug_repurposing']

# Get therapeutic area specific info
oncology_endpoints = guidelines['therapeutic_areas']['oncology']['endpoints']
```

## Market Intelligence Data

### Web Intelligence Sources
- **News APIs**: Reuters, Bloomberg, BioPharma Dive
- **Financial Data**: SEC filings, earnings reports
- **Scientific Literature**: PubMed, bioRxiv
- **Industry Reports**: Evaluate Pharma, GlobalData

### Data Processing Pipeline
```python
class MarketIntelligence:
    def gather_news(self, query: str, days: int = 30):
        """Gather recent news articles"""
        pass
    
    def analyze_sentiment(self, articles: List[str]):
        """Analyze market sentiment"""
        pass
    
    def extract_partnerships(self, text: str):
        """Extract partnership announcements"""
        pass
    
    def assess_competition(self, molecule: str, indication: str):
        """Assess competitive landscape"""
        pass
```

## Data Quality Standards

### Validation Rules
```python
def validate_clinical_trial(record: dict) -> bool:
    """Validate clinical trial record"""
    required_fields = ['nct_id', 'title', 'condition', 'intervention']
    
    # Check required fields
    for field in required_fields:
        if not record.get(field):
            return False
    
    # Validate NCT ID format
    if not record['nct_id'].startswith('NCT'):
        return False
    
    # Validate phase format
    valid_phases = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
    if record.get('phase') not in valid_phases:
        return False
    
    return True

def validate_patent(record: dict) -> bool:
    """Validate patent record"""
    required_fields = ['patent_number', 'title', 'assignee']
    
    for field in required_fields:
        if not record.get(field):
            return False
    
    # Validate date formats
    try:
        pd.to_datetime(record.get('filing_date'))
        pd.to_datetime(record.get('expiration_date'))
    except:
        return False
    
    return True
```

### Data Refresh Procedures
```python
class DataRefreshManager:
    def __init__(self):
        self.last_refresh = {}
    
    async def refresh_clinical_trials(self):
        """Refresh clinical trials data from API"""
        # Implementation for API calls
        pass
    
    async def refresh_patents(self):
        """Refresh patent data from API"""
        # Implementation for API calls
        pass
    
    def should_refresh(self, data_type: str, max_age_hours: int = 24) -> bool:
        """Check if data needs refreshing"""
        last_refresh = self.last_refresh.get(data_type)
        if not last_refresh:
            return True
        
        age = datetime.now() - last_refresh
        return age.total_seconds() > (max_age_hours * 3600)
```

## Sample Data Generation

### Mock Data Generators
```python
def generate_mock_trials(count: int = 100) -> pd.DataFrame:
    """Generate mock clinical trials data"""
    import random
    
    conditions = ['Alzheimer\'s Disease', 'Cancer', 'Diabetes', 'Hypertension']
    interventions = ['Aspirin', 'Metformin', 'Statins', 'ACE Inhibitors']
    phases = ['Phase 1', 'Phase 2', 'Phase 3']
    statuses = ['Recruiting', 'Active', 'Completed', 'Terminated']
    
    data = []
    for i in range(count):
        data.append({
            'nct_id': f'NCT{random.randint(10000000, 99999999)}',
            'title': f'Study of {random.choice(interventions)} in {random.choice(conditions)}',
            'condition': random.choice(conditions),
            'intervention': random.choice(interventions),
            'phase': random.choice(phases),
            'status': random.choice(statuses),
            'sponsor': f'Research Institute {i}',
            'enrollment': random.randint(50, 2000)
        })
    
    return pd.DataFrame(data)
```

## Integration Patterns

### API Integration Template
```python
class DataSourceAPI:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    async def search_trials(self, query: str, limit: int = 100) -> List[dict]:
        """Search clinical trials"""
        params = {
            'query': query,
            'limit': limit,
            'format': 'json'
        }
        
        response = await self.session.get(
            f"{self.base_url}/trials/search",
            params=params,
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        return response.json()
    
    async def get_patent_info(self, patent_number: str) -> dict:
        """Get patent details"""
        response = await self.session.get(
            f"{self.base_url}/patents/{patent_number}",
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        return response.json()
```