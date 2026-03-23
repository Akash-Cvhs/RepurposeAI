# 🚀 VHS Drug Repurposing Platform - Quick Start

## ✅ What's New: Unified Backend

The platform now runs on a **single backend server** - no need to manage multiple processes!

## 📋 Prerequisites

1. Python 3.9+ installed
2. API key configured in `.env` file:
   ```
   LLM_API_KEY=your_groq_api_key_here
   ```

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Backend

**Option A: Using batch file (Windows)**
```bash
# Double-click: start_backend.bat
```

**Option B: Using command line**
```bash
cd backend
python app.py
```

The backend will start on **http://localhost:8000**

### Step 3: Start Frontend

**Option A: Using batch file (Windows)**
```bash
# Double-click: start_frontend.bat
```

**Option B: Using command line**
```bash
cd frontend
streamlit run streamlit_app.py
```

The frontend will open automatically at **http://localhost:8501**

## 🧪 Test Backend Only

To test the backend without the frontend:

```bash
python quick_test.py
```

This will verify:
- ✅ Backend health
- ✅ All 6 MCP tools registered
- ✅ Full analysis workflow

## 🛠️ Available Tools

The unified backend includes 6 MCP tools:

1. **search_clinical_trials** - Search clinical trial databases
2. **search_patents** - Patent search & FTO analysis
3. **internal_rag** - Search internal documents
4. **gather_web_intelligence** - Market intelligence
5. **analyze_drug** - Drug analysis (SMILES, properties, images)
6. **generate_report** - Report generation

## 📊 API Endpoints

- `POST /run` - Execute drug analysis
- `GET /health` - Health check
- `GET /tools` - List available tools
- `GET /archives` - List previous reports
- `GET /docs` - Interactive API documentation

## 🔍 How It Works

1. **User submits query** via frontend
2. **LLM analyzes query** and creates execution plan
3. **Tools execute** via MCP protocol (parallel when possible)
4. **LLM synthesizes** results into comprehensive report
5. **Report saved** to `backend/archives/reports/`

## 📁 Project Structure

```
RepurposeAI/
├── backend/
│   ├── app.py                    # ⭐ Unified backend (single entry point)
│   ├── mcp/                      # MCP orchestration
│   │   ├── intelligent_orchestrator.py
│   │   └── server.py
│   ├── tools/                    # 6 MCP tools
│   ├── agents/                   # Legacy agents (not used)
│   ├── data/                     # Mock data & internal docs
│   └── archives/reports/         # Generated reports
├── frontend/
│   └── streamlit_app.py          # Streamlit UI
├── start_backend.bat             # Start backend
├── start_frontend.bat            # Start frontend
└── quick_test.py                 # Backend test script
```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify `.env` file exists with `LLM_API_KEY`
- Check Python version: `python --version` (need 3.9+)

### Frontend shows "Cannot connect to backend"
- Ensure backend is running on port 8000
- Check backend health: http://localhost:8000/health
- Look for errors in backend terminal

### Analysis returns empty report
- Check backend logs for errors
- Verify API key is valid (Groq)
- Test with simple query: "Analyze aspirin"

## 📚 Example Queries

Try these in the frontend:

1. **Simple drug analysis**
   - Query: "Analyze aspirin for cardiovascular disease"
   - Molecule: aspirin

2. **Disease-focused search**
   - Query: "Find treatments for Alzheimer's disease"
   - Molecule: (leave empty)

3. **Repurposing exploration**
   - Query: "Can metformin be repurposed for cancer treatment?"
   - Molecule: metformin

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Backend shows: "🚀 VHS Drug Repurposing Platform - Backend Starting"
- ✅ Backend shows: "📦 Registered Tools: ['internal_rag', 'search_clinical_trials', ...]"
- ✅ Frontend opens in browser automatically
- ✅ Submitting a query returns a comprehensive report
- ✅ Reports are saved to `backend/archives/reports/`

## 🔗 Useful Links

- Backend API Docs: http://localhost:8000/docs
- Backend Health: http://localhost:8000/health
- Frontend UI: http://localhost:8501

## 💡 Tips

- The first analysis may take 30-90 seconds (LLM planning + tool execution)
- Reports are saved as Markdown files in `backend/archives/reports/`
- You can download reports directly from the frontend
- Check `backend/archives/molecule_images/` for generated molecular structures

---

**Need help?** Check the logs in the terminal windows for detailed error messages.
