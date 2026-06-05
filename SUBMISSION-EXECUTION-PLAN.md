# Agentic Commerce on Arc - Submission Execution Plan

Status note: this historical submission plan has been reconciled with the
current code. The shipped build supports AI image generation, demo catalog
search, and Arc escrow transactions. NFT minting and marketplace listings are
not shipped.

## DEADLINE: January 23, 2026 (End of Online Phase)

---

## ASSET STATUS SUMMARY

| Asset | Status | Path |
|-------|--------|------|
| Cover Image (16:9) | READY | `docs/assets/cover-image-16x9.jpg` |
| Pitch Deck (PDF) | READY | `docs/assets/pitch-deck.pdf` |
| Demo Video (MP4) | NOT DONE | `video-demo/out/agentic-commerce-demo.mp4` |
| GitHub Repository | READY | https://github.com/DNYoussef/agentic-commerce-arc |
| README.md | READY | Complete with live URLs |
| Frontend (Live) | READY | https://frontend-production-dd6f.up.railway.app/ |
| Backend (Live) | READY | https://agentic-commerce-arc-production.up.railway.app/ |
| Smart Contract | READY | `SimpleEscrow` at `0x1D10c53dCa5931acdc8f6b8F9AA0ed674ae94171` |

---

## METICULOUS STEP-BY-STEP EXECUTION PLAN

### PHASE 1: VIDEO CREATION (Estimated: 1-2 hours)

#### Step 1.1: Pre-Recording Setup
**Type: BROWSER + CLI**

| # | Task | Type | Command/Action |
|---|------|------|----------------|
| 1 | Run warmup script | CLI | `powershell -File video-demo/scripts/pre-record-warmup.ps1` |
| 2 | Open OBS Studio | BROWSER | Launch OBS Studio manually |
| 3 | Configure OBS: 1920x1080, 30fps, MP4 output | BROWSER | OBS Settings > Output > Recording |
| 4 | Select browser window as source | BROWSER | OBS Sources > Window Capture |
| 5 | Set recording path | BROWSER | Output to: `D:\Projects\agentic-commerce-arc\video-demo\public\demo-recording.mp4` |

#### Step 1.2: Prepare Demo Environment
**Type: BROWSER**

| # | Task | Type | Notes |
|---|------|------|-------|
| 1 | Open frontend URL | BROWSER | https://frontend-production-dd6f.up.railway.app/ |
| 2 | Set browser zoom to 100% | BROWSER | Ctrl+0 |
| 3 | Clear browser cache | BROWSER | Ctrl+Shift+Delete |
| 4 | Connect MetaMask to Arc Testnet | BROWSER | Network: Arc Testnet (Chain ID: 5042002) |
| 5 | Ensure wallet has minimal balance | BROWSER | For transaction demos |
| 6 | Disable all notifications | BROWSER | Focus mode / DND |

#### Step 1.3: Record Demo
**Type: BROWSER**
Follow `video-demo/RECORDING-SCRIPT.md` exactly:

| Time | Scene | Action |
|------|-------|--------|
| 0:00-0:30 | App Overview | Pan across UI, show chat and marketplace |
| 0:30-1:30 | Describe Product | Type prompt, send message |
| 1:30-2:30 | AI Generation | Watch image generate (Replicate FLUX) |
| 2:30-3:00 | Wallet Connection | Connect MetaMask, show Arc Testnet |
| 3:00-3:45 | Purchase/Escrow | Click Purchase, confirm escrow transaction |
| 3:45-4:15 | Verify Explorer | Show transaction on Arc explorer |

**Target Duration: ~4 minutes raw footage**

#### Step 1.4: Edit Recording in DemoVideo.tsx
**Type: CLI**

```bash
# Edit DemoVideo.tsx to uncomment the OffthreadVideo section
# Lines 196-207: Remove the comment markers
```

**Manual edit required:**
1. Open `video-demo/src/DemoVideo.tsx`
2. Find lines 196-207 (the commented OffthreadVideo section)
3. Remove `{/* === UNCOMMENT WHEN RECORDING IS READY ===` and `=== END UNCOMMENT === */}`
4. Comment out the placeholder section (lines 209-230)

#### Step 1.5: Render Final Video
**Type: CLI**

```powershell
cd D:\Projects\agentic-commerce-arc\video-demo

# Preview first (opens browser)
npm run dev

# When satisfied, render final video
npm run build

# Or high quality render
npx remotion render src/index.ts DemoVideo out/agentic-commerce-demo.mp4 --codec=h264 --crf=18 --color-space=bt709
```

**Output:** `video-demo/out/agentic-commerce-demo.mp4`

---

### PHASE 2: FINAL VERIFICATION (Estimated: 15 minutes)

**Type: CLI**

```powershell
# Run verification script
powershell -File video-demo/scripts/verify-submission-assets.ps1
```

**Manual verification checklist:**

| # | Check | Expected |
|---|-------|----------|
| 1 | Video plays correctly | Full video, audio clear |
| 2 | Video duration | Under 5 minutes |
| 3 | No sensitive data visible | No private keys, seeds, passwords |
| 4 | Cover image is 16:9 | 1920x1080 |
| 5 | PDF opens correctly | 9 slides visible |
| 6 | Frontend URL works | https://frontend-production-dd6f.up.railway.app/ |
| 7 | Backend health check | https://agentic-commerce-arc-production.up.railway.app/health |

---

### PHASE 3: GIT COMMIT VIDEO (Estimated: 5 minutes)

**Type: CLI**

```bash
cd D:\Projects\agentic-commerce-arc

# Add video-demo folder (excluding node_modules and large recordings)
git add video-demo/src video-demo/package.json video-demo/tsconfig.json video-demo/*.md video-demo/remotion.config.ts video-demo/scripts

# Commit
git commit -m "feat: add Remotion video demo project for hackathon submission"

# Push
git push origin main
```

**NOTE:** Do NOT commit:
- `video-demo/node_modules/`
- `video-demo/public/demo-recording.mp4` (too large for git)
- `video-demo/out/` (rendered videos)

---

### PHASE 4: LABLAB.AI SUBMISSION (Estimated: 20 minutes)

**Type: BROWSER ONLY**

#### Step 4.1: Navigate to lablab.ai
1. Go to: https://lablab.ai/event/agentic-commerce-on-arc
2. Log in to your lablab.ai account
3. Find your team dashboard

#### Step 4.2: Locate Submit Button
1. Navigate to your team page
2. Click "Submit Project" or similar button
3. This opens the submission form

#### Step 4.3: Fill Submission Form

| Field | Value |
|-------|-------|
| **Project Title** | Agentic Commerce on Arc |
| **Short Description** | AI-powered product-concept assistant with Arc escrow transaction support |
| **Long Description** | See below |
| **Cover Image** | Upload: `docs/assets/cover-image-16x9.jpg` |
| **Demo Video** | Upload: `video-demo/out/agentic-commerce-demo.mp4` |
| **Pitch Deck** | Upload: `docs/assets/pitch-deck.pdf` |
| **GitHub Repository** | https://github.com/DNYoussef/agentic-commerce-arc |
| **Live Demo URL** | https://frontend-production-dd6f.up.railway.app/ |
| **Technologies Used** | Arc Blockchain, USDC, Replicate AI, React, FastAPI, Solidity |

**Long Description (copy-paste):**
```
Agentic Commerce on Arc is an AI-powered autonomous commerce platform built on the Arc blockchain.

Key Features:
- Natural language product requests via AI chat interface
- Autonomous AI image generation using Replicate FLUX
- Smart contract escrow for secure transactions
- Local demo catalog search with sorting and limits
- NFT minting, marketplace listings, and live retailer price quotes are not shipped

Technical Stack:
- Frontend: React 18 + TypeScript + Vite + TailwindCSS
- Backend: Python 3.11 + FastAPI + WebSocket streaming
- Blockchain: Arc (EVM-compatible, Chain ID: 5042002)
- AI: Replicate API (FLUX image generation)
- Smart Contracts: Solidity (SimpleEscrow)

Deployed Smart Contract: 0x1D10c53dCa5931acdc8f6b8F9AA0ed674ae94171

The platform demonstrates AI-assisted product creation and escrow transaction verification on Arc. It does not ship NFT minting or marketplace listing contracts.
```

#### Step 4.4: Submit
1. Review all fields
2. Click Submit
3. Save/screenshot confirmation

---

## CLI vs BROWSER SUMMARY

### CLI Tasks (I can help with)
| Task | Command |
|------|---------|
| Run warmup script | `powershell -File video-demo/scripts/pre-record-warmup.ps1` |
| Preview Remotion | `cd video-demo && npm run dev` |
| Render video | `cd video-demo && npm run build` |
| Verify assets | `powershell -File video-demo/scripts/verify-submission-assets.ps1` |
| Git commit | `git add ... && git commit && git push` |
| Check URLs | `curl https://frontend-production-dd6f.up.railway.app/` |

### BROWSER Tasks (Manual Required)
| Task | Why Manual |
|------|-----------|
| Open/configure OBS Studio | GUI application |
| Record screen demo | Requires UI interaction with app |
| Connect MetaMask wallet | Browser extension interaction |
| Perform demo transactions | Live blockchain interaction |
| Upload files to lablab.ai | File upload dialog |
| Fill lablab.ai submission form | Form fields |
| Submit to lablab.ai | Final submit button |

---

## EMERGENCY CONTACTS & BACKUP PLANS

### If Replicate is Slow
- Pre-generate an image before recording
- Have backup image URL ready

### If Arc RPC is Down
- Use alternative RPC endpoint
- Pre-record transaction segment

### If Recording Fails
- Use static screenshots with Ken Burns effect
- Narration can cover visual issues

### If lablab.ai Submission Issues
- Contact lablab.ai Discord support
- Manual submission window: 6 hours post-deadline

---

## QUICK START COMMANDS

```powershell
# 1. Warmup services
cd D:\Projects\agentic-commerce-arc
powershell -File video-demo/scripts/pre-record-warmup.ps1

# 2. After recording, uncomment video in DemoVideo.tsx, then:
cd video-demo
npm run build

# 3. Verify all assets
powershell -File scripts/verify-submission-assets.ps1

# 4. Commit (excluding large files)
cd D:\Projects\agentic-commerce-arc
git add video-demo/src video-demo/package.json video-demo/tsconfig.json video-demo/*.md video-demo/remotion.config.ts video-demo/scripts
git commit -m "feat: add Remotion video demo project"
git push
```

---

## FILE LOCATIONS SUMMARY

```
D:\Projects\agentic-commerce-arc\
|-- docs\assets\
|   |-- cover-image.jpg          # Original (1408x768)
|   |-- cover-image-16x9.jpg     # UPLOAD THIS (1920x1080)
|   +-- pitch-deck.pdf           # UPLOAD THIS
|
|-- video-demo\
|   |-- public\
|   |   +-- demo-recording.mp4   # YOUR RAW RECORDING GOES HERE
|   |
|   |-- out\
|   |   +-- agentic-commerce-demo.mp4  # UPLOAD THIS (rendered)
|   |
|   |-- scripts\
|   |   |-- pre-record-warmup.ps1
|   |   |-- render-video.ps1
|   |   +-- verify-submission-assets.ps1
|   |
|   +-- src\
|       |-- DemoVideo.tsx        # Main composition
|       |-- Intro.tsx            # Opening animation
|       +-- Outro.tsx            # Closing CTA
|
+-- SUBMISSION-EXECUTION-PLAN.md  # THIS FILE
```

---

**Last Updated:** 2026-01-22
**Deadline:** 2026-01-23 (End of Online Phase)
