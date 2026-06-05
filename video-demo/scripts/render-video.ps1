# Video Render Script
# Run after placing demo-recording.mp4 in public/

param(
    [switch]$Preview,
    [switch]$HighQuality
)

$projectPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$videoDemo = Join-Path $projectPath "video-demo"
$recording = Join-Path $videoDemo "public\demo-recording.mp4"
$output = Join-Path $videoDemo "out\agentic-commerce-demo.mp4"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ARC Video Render Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if recording exists
if (-not (Test-Path $recording)) {
    Write-Host "`nERROR: Screen recording not found!" -ForegroundColor Red
    Write-Host "Expected location: $recording"
    Write-Host "`nPlease:"
    Write-Host "  1. Record your demo using OBS (see RECORDING-SCRIPT.md)"
    Write-Host "  2. Save the recording to: public\demo-recording.mp4"
    exit 1
}

Write-Host "`nRecording found: $recording" -ForegroundColor Green

# Get recording info
$fileSize = (Get-Item $recording).Length / 1MB
Write-Host "File size: $([math]::Round($fileSize, 2)) MB"

# Check DemoVideo.tsx for uncommented video section
$demoVideo = Join-Path $videoDemo "src\DemoVideo.tsx"
$content = Get-Content $demoVideo -Raw
if ($content -match "/\* === UNCOMMENT WHEN RECORDING IS READY ===") {
    Write-Host "`nWARNING: OffthreadVideo section is still commented out!" -ForegroundColor Yellow
    Write-Host "Edit src/DemoVideo.tsx and uncomment the video section."
    exit 1
}

Set-Location $videoDemo

if ($Preview) {
    Write-Host "`nStarting Remotion Studio for preview..." -ForegroundColor Yellow
    npm run dev
} else {
    Write-Host "`nRendering final video..." -ForegroundColor Yellow

    if ($HighQuality) {
        # High quality render with CRF 18
        npx remotion render src/index.ts DemoVideo out/agentic-commerce-demo.mp4 --codec=h264 --crf=18 --color-space=bt709
    } else {
        # Standard render
        npm run build
    }

    if (Test-Path $output) {
        $outputSize = (Get-Item $output).Length / 1MB
        Write-Host "`nRender complete!" -ForegroundColor Green
        Write-Host "Output: $output"
        Write-Host "Size: $([math]::Round($outputSize, 2)) MB"

        # Open output folder
        Start-Process "explorer.exe" -ArgumentList "/select,`"$output`""
    } else {
        Write-Host "`nRender may have failed - output not found" -ForegroundColor Red
    }
}
