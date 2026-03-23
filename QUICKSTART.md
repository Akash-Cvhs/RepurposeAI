# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- LLM API key (Groq/OpenAI/Anthropic)
- 4GB RAM minimum

### Step 1: Clone & Configure
```bash
git clone <your-repo-url>
cd vhs-drug-repurposing

# Copy environment template
cp .env.example .env

# Edit with your API key
nano .env  # or use your favorite editor
# Change: LLM_API_KEY=your_actual_api_key
```

### Step 2: Start Services
```bash
# Build and start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Step 3: Test
```bash
# Wait 30 seconds for services to start, then:

# Test backend health
curl http://localhost/api/health

# Test MCP health
curl http://localhost/mcp/health

# Test drug search
curl -X POST http://localhost/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_smiles",
    "payload": {"query": "Alzheimer"},
    "session_id": "test"
  }'
```

### Step 4: Run Analysis
```bash
# Full drug repurposing analysis
curl -X POST http://localhost/mcp/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What drugs are available for Alzheimer'\''s disease?",
    "molecule": "Donepezil"
  }'
```

---

## 📁 Project Structure

```
vhs-drug-repurposing/
├── backend/
│   ├── agents/              # 7 specialized agents
│   ├── mcp/                 # MCP server & orchestration
│   ├── tools/               # RAG, SMILES analyzer
│   ├── middleware/          # Auth, confidence scoring
│   ├── utils/               # LLM, parsing, storage
│   ├── data/                # CSV, JSON, PDFs
│   ├── vectorstore/         # FAISS index
│   └── archives/            # Generated reports & images
├── frontend/                # Streamlit UI
├── docs/                    # Architecture & guides
├── tests/                   # Unit & integration tests
├── docker-compose.yml       # Container orchestration
├── nginx.conf               # Reverse proxy config
└── .env                     # Your configuration
```

---

## 🔧 Common Commands

### Docker Management
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart a service
docker compose restart backend

# View logs
docker compose logs -f backend

# Rebuild after code changes
docker compose up -d --build

# Scale backend
docker compose up -d --scale backend=3
```

### Database
```bash
# Access PostgreSQL
docker compose exec postgres psql -U vhs_user -d vhs_drug_db

# Backup database
docker compose exec postgres pg_dump -U vhs_user vhs_drug_db > backup.sql

# Restore database
docker compose exec -T postgres psql -U vhs_user vhs_drug_db < backup.sql
```

### Redis
```bash
# Access Redis CLI
docker compose exec redis redis-cli

# Check cache stats
docker compose exec redis redis-cli info stats

# Clear cache
docker compose exec redis redis-cli FLUSHDB
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend

# Follow with timestamps
docker compose logs -f -t backend
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check what's running
docker compose ps

# Check logs for errors
docker compose logs

# Remove everything and start fresh
docker compose down -v
docker compose up -d
```

### Port already in use
```bash
# Find what's using port 80
sudo lsof -i :80

# Kill the process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Out of memory
```bash
# Check resource usage
docker stats

# Add memory limits to docker-compose.yml:
services:
  backend:
    mem_limit: 2g
```

### Database connection failed
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

---

## 📊 Monitoring

### Health Checks
```bash
# Backend
curl http://localhost/api/health

# MCP
curl http://localhost/mcp/health

# Database
docker compose exec postgres pg_isready

# Redis
docker compose exec redis redis-cli ping
```

### Resource Usage
```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET_KEY` in .env
- [ ] Change `POSTGRES_PASSWORD` in .env
- [ ] Set `DEBUG=false` in .env
- [ ] Configure SSL/TLS (see DEPLOYMENT_GUIDE.md)
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up monitoring alerts
- [ ] Enable automated backups

---

## 📚 Next Steps

1. **Read Documentation**
   - `docs/ARCHITECTURE.md` - System design
   - `docs/DEPLOYMENT_GUIDE.md` - Production deployment
   - `docs/PRODUCTION_READINESS.md` - Production checklist

2. **Customize**
   - Add your own agents
   - Integrate real data sources
   - Customize confidence scoring

3. **Deploy**
   - Set up production server
   - Configure domain & SSL
   - Deploy frontend to Vercel

4. **Monitor**
   - Set up logging
   - Configure alerts
   - Track performance

---

## 🆘 Getting Help

- **Documentation:** See `docs/` folder
- **Issues:** Check GitHub issues
- **Logs:** `docker compose logs -f`
- **Health:** `curl http://localhost/api/health`

---

## 🎯 Quick Test Queries

### Test Drug Search
```bash
curl -X POST http://localhost/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_smiles",
    "payload": {"query": "Alzheimer"},
    "session_id": "test"
  }'
```

### Test Drug Analysis
```bash
curl -X POST http://localhost/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "analyze_smiles",
    "payload": {
      "smiles": "CC(C)NCC(COc1ccccc1CC=C)O",
      "include_admet": true
    },
    "session_id": "test"
  }'
```

### Test Internal RAG
```bash
curl -X POST http://localhost/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "internal_rag",
    "payload": {
      "query": "clinical trial results",
      "top_k": 5
    },
    "session_id": "test"
  }'
```

### Test Full Orchestration
```bash
curl -X POST http://localhost/mcp/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze Donepezil for Alzheimer'\''s treatment",
    "molecule": "Donepezil"
  }'
```

---

Happy coding! 🚀
