# Deployment Guide: Docker + Vercel

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                         VERCEL                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Frontend (Next.js/Streamlit via iframe)              │  │
│  │  - Static assets                                       │  │
│  │  - API routes (lightweight only)                       │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS API Calls
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    YOUR SERVER (Docker)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy + Load Balancer)                │  │
│  │  - SSL/TLS termination                                 │  │
│  │  - Rate limiting                                       │  │
│  │  - Request routing                                     │  │
│  └──────────────┬─────────────────────────┬───────────────┘  │
│                 │                         │                   │
│     ┌───────────▼──────────┐  ┌──────────▼────────────┐      │
│     │  Backend API         │  │  MCP Server           │      │
│     │  (FastAPI:8000)      │  │  (FastAPI:8001)       │      │
│     │  - Main workflow     │  │  - Tool orchestration │      │
│     │  - Report generation │  │  - Agent routing      │      │
│     └──────────┬───────────┘  └──────────┬────────────┘      │
│                │                         │                   │
│     ┌──────────▼──────────────────────────▼────────────┐      │
│     │  Redis (Cache + Message Queue)                   │      │
│     │  - Tool result caching                           │      │
│     │  - Session management                            │      │
│     │  - Celery broker                                 │      │
│     └──────────────────────────────────────────────────┘      │
│                                                               │
│     ┌──────────────────────────────────────────────────┐      │
│     │  PostgreSQL (Primary Database)                   │      │
│     │  - User accounts                                 │      │
│     │  - Run history                                   │      │
│     │  - Confidence scores                             │      │
│     │  - Audit logs                                    │      │
│     └──────────────────────────────────────────────────┘      │
│                                                               │
│     ┌──────────────────────────────────────────────────┐      │
│     │  FAISS Vector Store (Mounted Volume)             │      │
│     │  - Internal document embeddings                  │      │
│     └──────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

---

## Why This Architecture?

### Vercel Limitations for Backend
❌ **Cannot deploy FastAPI backend on Vercel because:**
1. **Timeout:** 10s for Hobby, 60s for Pro (your agents take 30-120s)
2. **No persistent storage:** Vector stores need persistent volumes
3. **No background jobs:** Can't run Celery workers
4. **Cold starts:** Slow for ML models
5. **Cost:** Expensive for compute-heavy workloads

✅ **What Vercel IS good for:**
- Static frontend hosting
- Serverless API routes (lightweight only)
- CDN for assets
- Edge functions for auth

### Server (Docker) for Backend
✅ **Perfect for:**
- Long-running agent workflows
- Persistent vector stores
- Background job processing
- WebSocket connections
- Full control over resources

---

## Deployment Options

### Option 1: Hybrid (Recommended)
```
Frontend → Vercel (free/cheap)
Backend → Your Server (Docker)
```
**Pros:** Best performance, lowest cost, full control
**Cons:** Need to manage server

### Option 2: All-in-One Server
```
Frontend + Backend → Your Server (Docker)
```
**Pros:** Simplest, no CORS issues
**Cons:** No CDN benefits, single point of failure

### Option 3: Full Cloud
```
Frontend → Vercel
Backend → AWS ECS / GCP Cloud Run / Azure Container Apps
Database → Managed services
```
**Pros:** Fully managed, auto-scaling
**Cons:** Most expensive ($500-2000/month)

---

## Server Requirements

### Minimum (Development)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 20GB SSD
- **Cost:** ~$10-20/month (Hetzner, Contabo)

### Recommended (Production)
- **CPU:** 4-8 cores
- **RAM:** 16GB
- **Storage:** 100GB SSD
- **Cost:** ~$50-100/month (DigitalOcean, Linode, Vultr)

### High Performance
- **CPU:** 8-16 cores
- **RAM:** 32GB
- **Storage:** 200GB NVMe SSD
- **Cost:** ~$200-400/month

---

## Docker Compose Setup

See `docker-compose.yml` (will create next)

---

## Environment Variables

### Backend (.env)
```bash
# LLM
LLM_API_KEY=gsk_xxxxx
DEFAULT_LLM_MODEL=openai/gpt-oss-20b

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/vhs_drug_db
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
MCP_PORT=8001
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO
```

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_MCP_URL=https://api.yourdomain.com/mcp
```

---

## Deployment Steps

### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Create app directory
mkdir -p /opt/vhs-drug-repurposing
cd /opt/vhs-drug-repurposing

# Clone repository
git clone <your-repo-url> .

# Create .env file
cp .env.example .env
nano .env  # Edit with your values
```

### 2. Build and Run

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Check logs
docker compose logs -f

# Check status
docker compose ps
```

### 3. SSL/TLS Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### 4. Nginx Configuration

See `nginx.conf` (will create next)

### 5. Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl https://api.yourdomain.com/health

# MCP health
curl https://api.yourdomain.com/mcp/health

# Database connection
docker compose exec postgres pg_isready

# Redis connection
docker compose exec redis redis-cli ping
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

### Backups
```bash
# Database backup
docker compose exec postgres pg_dump -U user vhs_drug_db > backup.sql

# Vector store backup
tar -czf vectorstore_backup.tar.gz backend/vectorstore/

# Restore database
docker compose exec -T postgres psql -U user vhs_drug_db < backup.sql
```

### Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build

# Zero-downtime deployment (with multiple replicas)
docker compose up -d --scale backend=2 --no-recreate
docker compose up -d --scale backend=1
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable firewall (UFW)
- [ ] Configure fail2ban
- [ ] Set up SSL/TLS
- [ ] Enable JWT authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring alerts
- [ ] Regular security updates
- [ ] Backup automation
- [ ] Audit log review

---

## Cost Breakdown

### Server Hosting
- **Hetzner CPX31:** €11.90/month (4 vCPU, 8GB RAM)
- **DigitalOcean:** $48/month (4 vCPU, 8GB RAM)
- **Linode:** $48/month (4 vCPU, 8GB RAM)
- **Vultr:** $48/month (4 vCPU, 8GB RAM)

### Vercel
- **Hobby:** Free (100GB bandwidth)
- **Pro:** $20/month (1TB bandwidth)

### Domain & SSL
- **Domain:** $10-15/year
- **SSL:** Free (Let's Encrypt)

### Total Monthly Cost
- **Minimum:** $10-20 (server) + $0 (Vercel free)
- **Recommended:** $50 (server) + $0-20 (Vercel)
- **With managed DB:** +$15-50 (managed PostgreSQL/Redis)

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Check environment variables
docker compose exec backend env | grep LLM

# Restart service
docker compose restart backend
```

### Database connection failed
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check connection
docker compose exec backend python -c "from config import DATABASE_URL; print(DATABASE_URL)"

# Reset database
docker compose down -v
docker compose up -d
```

### High memory usage
```bash
# Check resource usage
docker stats

# Limit container memory
# Add to docker-compose.yml:
# mem_limit: 2g
```

### Slow performance
```bash
# Check Redis cache hit rate
docker compose exec redis redis-cli info stats | grep hit

# Check database query performance
docker compose exec postgres psql -U user -d vhs_drug_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Scale backend
docker compose up -d --scale backend=3
```

---

## Next Steps

1. Create Docker configuration files
2. Implement JWT authentication
3. Add confidence scoring system
4. Set up monitoring
5. Deploy to server
6. Configure Vercel frontend
