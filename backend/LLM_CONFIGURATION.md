# LLM Configuration

## ✅ Configured

Your project now uses `LLM_API_KEY` from `.env` across all agents.

## Current Setup

**Provider:** Groq  
**Model:** llama-3.1-70b-versatile  
**API Key:** gsk_tveSuIgC6xJ4qNKW... (detected automatically)

## How It Works

1. **`.env` file** contains `LLM_API_KEY=gsk_...`
2. **`config.py`** auto-detects provider based on key prefix:
   - `gsk_` → Groq
   - `sk-` → OpenAI
   - `sk-ant-` → Anthropic
3. **`utils/llm_utils.py`** provides `get_llm()` function
4. **All agents** use `get_llm()` instead of hardcoded ChatOpenAI

## Supported Providers

| Provider | Key Prefix | Default Model |
|----------|-----------|---------------|
| Groq | `gsk_` | llama-3.1-70b-versatile |
| OpenAI | `sk-` | gpt-4 |
| Anthropic | `sk-ant-` | claude-3-5-sonnet-20241022 |

## Files Updated

✅ `backend/config.py` - Auto-detection logic  
✅ `backend/utils/llm_utils.py` - Unified LLM interface  
✅ `backend/agents/master_agent.py`  
✅ `backend/agents/clinical_trials_agent.py`  
✅ `backend/agents/patent_agent.py`  
✅ `backend/agents/internal_insights_agent.py`  
✅ `backend/agents/web_intel_agent.py`  
✅ `backend/agents/drug_analyzer_agent.py`  
✅ `backend/agents/report_generator_agent.py`  
✅ `backend/mcp/orchestrator.py`  
✅ `backend/requirements.txt` - Added langchain-groq

## Switching Providers

Just change `LLM_API_KEY` in `.env`:

```bash
# Use Groq
LLM_API_KEY=gsk_your_groq_key_here

# Use OpenAI
LLM_API_KEY=sk-your_openai_key_here

# Use Anthropic
LLM_API_KEY=sk-ant-your_anthropic_key_here
```

No code changes needed!

## Testing

```bash
cd backend
python -c "from config import LLM_PROVIDER, DEFAULT_LLM_MODEL; print(f'{LLM_PROVIDER}: {DEFAULT_LLM_MODEL}')"
```

Expected output:
```
groq: llama-3.1-70b-versatile
```
