# Data Sources and Schemas

For this prototype, we use **mock CSV/JSON files** under `backend/data/`.
They simulate real systems like ClinicalTrials.gov, patent databases, and guidelines.

---

## `trials.csv` (mock ClinicalTrials.gov)

Location: `backend/data/trials.csv`

Suggested columns:

- `nct_id`: string - trial ID
- `title`: string - brief title
- `molecule`: string - primary molecule name
- `condition`: string - disease / indication
- `phase`: string - e.g., "Phase 2", "Phase 3"
- `status`: string - e.g., "Recruiting", "Completed", "Terminated"
- `start_date`: string - ISO or human-readable date
- `completion_date`: string - ISO or human-readable date
- `location`: string - optional (country/region)
- `sponsor`: string - optional

Example row (conceptual):

```csv
nct_id,title,molecule,condition,phase,status,start_date,completion_date,location,sponsor
NCT00000001,Metformin in Breast Cancer,metformin,breast cancer,Phase 2,Recruiting,2024-01-01,2026-06-01,US,Example Pharma
```

Agents:

- `clinical_trials_agent` should:
  - Load this CSV
  - Filter by `molecule` and/or `condition`
  - Return a structured list of dicts under `state["trials"]`
  - Optionally compute summary stats (trials per phase/status)

---

## `patents.csv` (mock patent landscape)

Location: `backend/data/patents.csv`

Suggested columns:

- `patent_id`: string - e.g., "US1234567"
- `title`: string
- `molecule`: string - main molecule name
- `moa`: string - mechanism of action (optional)
- `jurisdiction`: string - e.g., "US", "EU"
- `expiry_date`: string - ISO date (used for FTO)
- `assignee`: string - patent owner
- `claims_summary`: string - short textual summary

Example row:

```csv
patent_id,title,molecule,moa,jurisdiction,expiry_date,assignee,claims_summary
US1234567,Use of Metformin in Oncology,metformin,AMPK modulator,US,2030-12-31,Example Pharma,Method of treating solid tumors with metformin.
```

Agents:

- `patent_agent` should:
  - Load this CSV
  - Filter by `molecule` (and optionally `moa`)
  - Compute a simple FTO risk:
    - Most patents expired -> `low`
    - Mix of active and expiring soon -> `medium`
    - Many active, long expiry -> `high`
  - Set `state["patents"]` and `state["fto_risk"]`

---

## `guidelines.json` (mock guidelines / RWE)

Location: `backend/data/guidelines.json`

Suggested structure (list of objects):

```json
[
  {
    "id": "guideline-1",
    "disease": "type 2 diabetes",
    "molecule": "metformin",
    "guideline_title": "First-line therapy for type 2 diabetes",
    "summary": "Metformin is recommended as first-line therapy for most patients...",
    "source": "Mock ADA Guidelines",
    "url": "https://example.org/guidelines/metformin-diabetes"
  },
  {
    "id": "guideline-2",
    "disease": "breast cancer",
    "molecule": "metformin",
    "guideline_title": "Off-label considerations for metformin in oncology",
    "summary": "Preliminary evidence suggests potential benefit of metformin in certain breast cancer subtypes...",
    "source": "Mock Oncology Review",
    "url": "https://example.org/rwe/metformin-oncology"
  }
]
```

Agents:

- `web_intel_agent` should:
  - Load this JSON
  - Filter entries by `molecule` and/or `disease`
  - Build a readable text or bullet-list summary under `state["web_findings"]`
  - Prefer to include `url` fields so the report can show source links

---

## Other optional mock data

You may add more JSON/CSV files, for example:

- `rwe_news.json` - mock real-world evidence / news
- `safety_signals.csv` - mock safety/AE signals
- `unmet_needs.json` - pre-defined unmet needs per indication

If you add new files, update this document and ensure the relevant agent reads from them.
