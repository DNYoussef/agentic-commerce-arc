# Pre-Recording Warmup Script
# Run this 15 minutes before recording to warm up services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ARC Demo Pre-Recording Warmup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Test Backend Health
Write-Host "`n[1/4] Testing Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://agentic-commerce-arc-production.up.railway.app/health" -TimeoutSec 10
    Write-Host "  Backend: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "  Backend: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Test Frontend
Write-Host "`n[2/4] Testing Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://frontend-production-dd6f.up.railway.app/" -TimeoutSec 10 -UseBasicParsing
    Write-Host "  Frontend: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  Frontend: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Test Arc RPC (basic connection)
Write-Host "`n[3/4] Testing Arc Testnet RPC..." -ForegroundColor Yellow
try {
    $body = @{
        jsonrpc = "2.0"
        method = "eth_chainId"
        params = @()
        id = 1
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "https://rpc-testnet.arc.tech" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    if ($response.result -eq "0x4CEEE2") {
        Write-Host "  Arc Testnet RPC: CONNECTED (Chain ID: 5042002)" -ForegroundColor Green
    } else {
        Write-Host "  Arc Testnet RPC: Unexpected chain ID $($response.result)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Arc Testnet RPC: FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Open Frontend in Browser
Write-Host "`n[4/4] Opening Frontend in Browser..." -ForegroundColor Yellow
Start-Process "https://frontend-production-dd6f.up.railway.app/"
Write-Host "  Browser opened" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Warmup Complete - Ready to Record!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:"
Write-Host "  1. Open OBS Studio"
Write-Host "  2. Set resolution to 1920x1080, 30fps"
Write-Host "  3. Wait 2-3 minutes for services to stay warm"
Write-Host "  4. Start recording!"
