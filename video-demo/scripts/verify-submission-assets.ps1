# Submission Assets Verification Script
# Run before submitting to lablab.ai

$projectPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " lablab.ai Submission Asset Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allGood = $true

# 1. Cover Image (16:9 JPG/PNG)
Write-Host "`n[1/5] Cover Image" -ForegroundColor Yellow
$coverImage = Join-Path $projectPath "docs\assets\cover-image.jpg"
if (Test-Path $coverImage) {
    $size = (Get-Item $coverImage).Length / 1KB
    Write-Host "  Found: cover-image.jpg ($([math]::Round($size, 1)) KB)" -ForegroundColor Green
    Write-Host "  Path: $coverImage"
    # Note: Image is 1408x768 (close to 16:9)
} else {
    Write-Host "  MISSING: Cover image not found!" -ForegroundColor Red
    $allGood = $false
}

# 2. Pitch Deck PDF
Write-Host "`n[2/5] Pitch Deck (PDF)" -ForegroundColor Yellow
$pitchDeck = Join-Path $projectPath "docs\assets\pitch-deck.pdf"
if (Test-Path $pitchDeck) {
    $size = (Get-Item $pitchDeck).Length / 1MB
    Write-Host "  Found: pitch-deck.pdf ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    Write-Host "  Path: $pitchDeck"
} else {
    Write-Host "  MISSING: Pitch deck PDF not found!" -ForegroundColor Red
    $allGood = $false
}

# 3. Demo Video (MP4)
Write-Host "`n[3/5] Demo Video (MP4)" -ForegroundColor Yellow
$videoDemo = Join-Path $projectPath "video-demo\out\agentic-commerce-demo.mp4"
if (Test-Path $videoDemo) {
    $size = (Get-Item $videoDemo).Length / 1MB
    Write-Host "  Found: agentic-commerce-demo.mp4 ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    Write-Host "  Path: $videoDemo"
} else {
    Write-Host "  MISSING: Demo video not found!" -ForegroundColor Red
    Write-Host "  Expected: $videoDemo"
    $allGood = $false
}

# 4. GitHub Repository
Write-Host "`n[4/5] GitHub Repository" -ForegroundColor Yellow
$gitRemote = git -C $projectPath remote get-url origin 2>$null
if ($gitRemote) {
    Write-Host "  Remote: $gitRemote" -ForegroundColor Green
    # Check if public
    $repoUrl = $gitRemote -replace "\.git$", ""
    Write-Host "  URL: $repoUrl"
} else {
    Write-Host "  MISSING: No git remote configured!" -ForegroundColor Red
    $allGood = $false
}

# 5. Live URLs
Write-Host "`n[5/5] Live Demo URLs" -ForegroundColor Yellow
$frontendUrl = "https://frontend-production-dd6f.up.railway.app/"
$backendUrl = "https://agentic-commerce-arc-production.up.railway.app/health"

try {
    $response = Invoke-WebRequest -Uri $frontendUrl -TimeoutSec 10 -UseBasicParsing
    Write-Host "  Frontend: HTTP $($response.StatusCode) - $frontendUrl" -ForegroundColor Green
} catch {
    Write-Host "  Frontend: UNREACHABLE - $frontendUrl" -ForegroundColor Red
    $allGood = $false
}

try {
    $response = Invoke-RestMethod -Uri $backendUrl -TimeoutSec 10
    Write-Host "  Backend: HEALTHY - $backendUrl" -ForegroundColor Green
} catch {
    Write-Host "  Backend: UNREACHABLE - $backendUrl" -ForegroundColor Red
    $allGood = $false
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host " ALL ASSETS READY FOR SUBMISSION!" -ForegroundColor Green
} else {
    Write-Host " SOME ASSETS MISSING - See above" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

# Submission Checklist
Write-Host "`nSubmission Info for lablab.ai:"
Write-Host "  Project Title: Agentic Commerce on Arc"
Write-Host "  GitHub: https://github.com/DNYoussef/agentic-commerce-arc"
Write-Host "  Contract: 0x1D10c53dCa5931acdc8f6b8F9AA0ed674ae94171"
Write-Host "  Network: Arc Testnet (Chain ID: 5042002)"
Write-Host "  Live Demo: $frontendUrl"

return $allGood
