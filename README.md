# Agentic Commerce on Arc

## Canonical Status

<!-- STATUS:START -->
Canonical status from `2026-EXOSKELETON-STATUS.json`.

Status: 95% (source: implementation-plan)
Registry refreshed: 2026-01-13T17:58:23.788789+00:00
Signals: git=yes, tests=yes, ci=yes, readme=yes, last_commit=089ee3e
<!-- STATUS:END -->


> AI-powered autonomous commerce platform built on the Arc blockchain

[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/template)
[![Tests](https://github.com/yourusername/agentic-commerce-arc/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/agentic-commerce-arc/actions/workflows/test.yml)
[![Contracts](https://github.com/yourusername/agentic-commerce-arc/actions/workflows/contracts.yml/badge.svg)](https://github.com/yourusername/agentic-commerce-arc/actions/workflows/contracts.yml)

## Overview

Agentic Commerce on Arc is an autonomous AI agent that can:
- Generate product images using AI (Replicate)
- Create and manage NFT listings on the Arc blockchain
- Handle purchases and transactions autonomously
- Interact with users through natural language

Built for the [lablab.ai Agentic Commerce Hackathon](https://lablab.ai/event/agentic-commerce-on-arc).

## Architecture

```
+------------------+     +------------------+     +------------------+
|    Frontend      |     |    Backend       |     |  Arc Blockchain  |
|   (React/Vite)   |<--->|   (FastAPI)      |<--->|  (Smart Contracts)|
+------------------+     +------------------+     +------------------+
        |                       |                        |
        |                       v                        |
        |                +------------------+            |
        |                |   AI Services    |            |
        |                |   (Replicate)    |            |
        |                +------------------+            |
        |                                               |
        +-----------------------------------------------+
                    WalletConnect / Web3
```

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Blockchain**: Arc (EVM-compatible) + Foundry + Solidity
- **AI**: Replicate API (FLUX, Stable Diffusion)
- **Infrastructure**: Railway + GitHub Actions

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Foundry (for smart contracts)
- Docker (optional, for local development)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/agentic-commerce-arc.git
cd agentic-commerce-arc
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Option A: Docker Compose (Recommended)

```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Option B: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Smart Contracts:**
```bash
cd contracts
forge install
forge build
forge test
```

## Project Structure

```
agentic-commerce-arc/
|-- .github/
|   +-- workflows/
|       |-- deploy.yml      # Railway deployment
|       |-- test.yml        # Test suite
|       +-- contracts.yml   # Foundry tests
|-- backend/
|   |-- main.py            # FastAPI application
|   |-- models/            # SQLAlchemy models
|   |-- routers/           # API endpoints
|   |-- services/          # Business logic
|   +-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- components/    # React components
|   |   |-- hooks/         # Custom hooks
|   |   |-- pages/         # Page components
|   |   +-- services/      # API clients
|   +-- package.json
|-- contracts/
|   |-- src/               # Solidity contracts
|   |-- test/              # Foundry tests
|   +-- foundry.toml
|-- docker-compose.yml
|-- .env.example
+-- README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/generate` | Generate AI image |
| POST | `/api/mint` | Mint NFT |
| GET | `/api/listings` | Get all listings |
| POST | `/api/purchase` | Purchase listing |
| GET | `/api/agent/status` | Agent status |

## Smart Contracts

The platform uses the following contracts on Arc:

- **AgentNFT.sol** - ERC721 for AI-generated products
- **Marketplace.sol** - Listing and purchase logic
- **AgentWallet.sol** - Autonomous agent wallet

### Deploying Contracts

```bash
cd contracts

# Deploy to local Anvil
forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast

# Deploy to Arc testnet
forge script script/Deploy.s.sol --rpc-url $ALCHEMY_ARC_RPC --broadcast --verify
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REPLICATE_API_TOKEN` | Replicate API key | Yes |
| `ALCHEMY_ARC_RPC` | Arc RPC endpoint | Yes |
| `WALLETCONNECT_PROJECT_ID` | WalletConnect project ID | Yes |
| `AGENT_PRIVATE_KEY` | Agent wallet private key | Yes |
| `DATABASE_URL` | Database connection string | No |

## Deployment

### Railway (Recommended)

1. Fork this repository
2. Connect to Railway
3. Set environment variables in Railway dashboard
4. Deploy!

GitHub Actions will automatically deploy on push to `main`.

### Manual Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test

# Contract tests
cd contracts
forge test -vvv
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Hackathon Links

- [lablab.ai Event Page](https://lablab.ai/event/agentic-commerce-on-arc)
- [Arc Documentation](https://docs.arc.xyz)
- [Replicate API](https://replicate.com/docs)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Team

Built with passion for the Agentic Commerce on Arc Hackathon.

---

**Note**: This project is a hackathon submission. Use at your own risk in production environments.