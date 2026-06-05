# Agentic Commerce on Arc

![Agentic Commerce Cover](docs/assets/cover-image.jpg)

## Canonical Status

<!-- STATUS:START -->
Canonical status from `2026-EXOSKELETON-STATUS.json`.

Status: 95% (source: implementation-plan)
Registry refreshed: 2026-01-15T20:37:16.435423+00:00
Signals: git=yes, tests=yes, ci=yes, readme=yes, last_commit=224a87f
<!-- STATUS:END -->


> AI-powered product-concept assistant with Arc escrow transaction support

[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/template)
[![Tests](https://github.com/DNYoussef/agentic-commerce-arc/actions/workflows/test.yml/badge.svg)](https://github.com/DNYoussef/agentic-commerce-arc/actions/workflows/test.yml)
[![Contracts](https://github.com/DNYoussef/agentic-commerce-arc/actions/workflows/contracts.yml/badge.svg)](https://github.com/DNYoussef/agentic-commerce-arc/actions/workflows/contracts.yml)

## Overview

Agentic Commerce on Arc is an autonomous AI agent that can:
- Generate product images using AI (Replicate)
- Search a local demo product catalog with filters, sorting, and limits
- Verify and record Arc escrow transactions
- Interact with users through natural language

Current limitation: NFT minting, marketplace listings, and live retailer price
quotes are not shipped in this build. Price comparison returns an explicit
unavailable status unless `PRICE_COMPARE_MODE=demo` is deliberately enabled for
synthetic UI exercises.

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
git clone https://github.com/DNYoussef/agentic-commerce-arc.git
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
| POST | `/auth/register` | Register and receive tokens |
| POST | `/auth/login` | Login and receive tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/chat` | Process an authenticated chat message |
| POST | `/products/search` | Search the local demo catalog |
| POST | `/products/compare` | Return live-price unavailable status or labeled demo prices |
| POST | `/transactions/verify` | Verify an Arc escrow transaction |
| POST | `/images/generate` | Generate an AI product image |
| WS | `/ws/chat/{user_id}` | Authenticated streaming chat |

## Smart Contracts

The platform uses the following contract on Arc:

- **SimpleEscrow.sol** - ETH/ARC escrow between buyer and seller with release/refund logic

No ERC721 NFT minting contract, marketplace contract, or autonomous agent wallet
contract is present in this repository.

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
| `ALCHEMY_ARC_RPC` or `ARC_RPC_URL` | Arc RPC endpoint for transaction verification | Yes for chain verification |
| `WALLETCONNECT_PROJECT_ID` | WalletConnect project ID | Yes |
| `ESCROW_CONTRACT` / `NEXT_PUBLIC_ESCROW_CONTRACT` | Deployed SimpleEscrow contract address | Yes for purchase/verify flows |
| `NEXT_PUBLIC_ESCROW_SELLER` | Seller address used by the demo purchase UI | Yes for purchase flow |
| `PRICE_COMPARE_MODE` | Optional `demo` mode for labeled synthetic prices | No |
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

## Live Demo

- **Frontend**: https://frontend-production-dd6f.up.railway.app/
- **Backend API**: https://agentic-commerce-arc-production.up.railway.app/
- **API Docs**: https://agentic-commerce-arc-production.up.railway.app/docs

### Deployed Escrow Contract

- **Contract Address**: `0x1D10c53dCa5931acdc8f6b8F9AA0ed674ae94171`
- **Network**: Arc Testnet (Chain ID: 5042002)
- **Contract Type**: `SimpleEscrow`

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
