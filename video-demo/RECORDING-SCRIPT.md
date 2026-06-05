# ARC Demo Video Recording Script

## Pre-Recording Checklist

### Environment Setup
- [ ] OBS Studio installed and configured (1920x1080, 30fps)
- [ ] Browser zoomed to 100% (Ctrl+0)
- [ ] MetaMask installed with Arc Testnet configured
- [ ] Throwaway wallet connected (minimal balance)
- [ ] All notifications disabled (Focus mode on)

### Service Warmup (Run 15 min before recording)
```powershell
# Test backend health
curl https://agentic-commerce-arc-production.up.railway.app/health

# Test frontend loads
Start-Process "https://frontend-production-dd6f.up.railway.app/"

# Warm up Replicate (hit generate endpoint once)
# This prevents cold start delays during recording
```

### Pre-fetch Safety Assets
- [ ] Screenshot of a successful transaction on Arc explorer
- [ ] Pre-generated image URL (backup if Replicate is slow)
- [ ] Transaction hash from previous successful escrow transaction (backup)

---

## Recording Timeline (Target: 4 minutes raw)

### Scene 1: App Overview (0:00 - 0:30)
**Actions:**
1. Open frontend URL in browser
2. Pan slowly across the UI
3. Show the chat interface
4. Show marketplace/listings area

**Say (or add as voiceover later):**
> "Agentic Commerce on Arc - an AI-powered autonomous commerce platform."

---

### Scene 2: Describe Product (0:30 - 1:30)
**Actions:**
1. Click on chat input
2. Type slowly: "Create a futuristic sneaker with holographic panels and neon accents"
3. Press Enter/Send
4. Wait for AI to acknowledge

**Key moments to capture:**
- Typing animation
- Message appearing in chat
- AI agent responding

**Say:**
> "I simply describe what I want in natural language."

---

### Scene 3: AI Image Generation (1:30 - 2:30)
**Actions:**
1. Watch AI generate image (Replicate FLUX)
2. Show loading state
3. Show generated image appearing
4. React positively (pause on the result)

**Key moments to capture:**
- Loading/generating indicator
- Image appearing
- Final result display

**Say:**
> "The AI agent generates a unique product image using FLUX."

**BACKUP PLAN:** If Replicate is slow (>30 sec), cut here and splice with pre-generated image.

---

### Scene 4: Wallet Connection (2:30 - 3:00)
**Actions:**
1. Click "Connect Wallet" if not connected
2. MetaMask popup appears
3. Select account
4. Confirm connection
5. Show connected state with wallet address

**Key moments to capture:**
- MetaMask popup
- Network showing "Arc Testnet"
- Connected indicator

**Say:**
> "I connect my wallet to the Arc blockchain - a stablecoin-native chain."

---

### Scene 5: Purchase/Escrow Flow (3:00 - 3:45)
**Actions:**
1. Click "Purchase" or "Mint" button
2. PurchaseModal opens showing:
   - Product image
   - Price in ETH
   - Gas estimate
3. If needed, click "Approve Token"
4. Click "Confirm Purchase"
5. MetaMask transaction popup
6. Confirm transaction
7. Wait for confirmation
8. Success state

**Key moments to capture:**
- Modal with price and gas
- MetaMask transaction details
- "Pending" state
- "Confirmed" success message

**Say:**
> "One click creates an escrow transaction on Arc. The smart contract secures my payment until delivery."

---

### Scene 6: Verify on Explorer (3:45 - 4:15)
**Actions:**
1. Click transaction hash link (or open explorer manually)
2. Show Arc Testnet Explorer
3. Point to:
   - Transaction hash
   - From/To addresses
   - Value transferred
   - Status: Success
4. Scroll to show contract interaction

**Say:**
> "The transaction is confirmed on Arc Testnet. Fully autonomous commerce."

**Explorer URL:** https://testnet.arcscan.app/tx/{TX_HASH}

---

## Post-Recording Assembly

### File Placement
```
video-demo/
  public/
    demo-recording.mp4    <-- Place your OBS recording here
```

### Uncomment Video Import
Edit `src/DemoVideo.tsx`:
1. Uncomment the `<Video>` component section
2. Comment out the placeholder section
3. Adjust Sequence timing if needed

### Render Commands
```powershell
cd D:\Projects\agentic-commerce-arc\video-demo

# Preview in browser
npm run dev

# List compositions
npm run compositions

# Render full video
npm run build

# Output: out/agentic-commerce-demo.mp4
```

### Final Checklist
- [ ] Video is under 4:30 (buffer for 5:00 limit)
- [ ] Audio levels are consistent
- [ ] No private keys/seeds visible
- [ ] Text overlays are legible
- [ ] Transitions are smooth
- [ ] Watch full video end-to-end before submission

---

## Emergency Backup Plan

If live demo fails during recording:

1. **Use pre-recorded clips:**
   - Have 3-4 short clips of successful interactions ready
   - Splice them together in editing

2. **Narration saves everything:**
   - Strong voiceover can cover visual hiccups
   - Focus on the story, not perfect UI

3. **Static screenshots with Ken Burns:**
   - Pan/zoom over screenshots if video fails
   - Still shows the functionality

4. **Honest acknowledgment:**
   - "Here's what the successful flow looks like..."
   - Judges appreciate authenticity
