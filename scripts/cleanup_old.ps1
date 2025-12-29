# Novel Assistant - Clean Old Installation (PowerShell)
# =====================================================
#
# Run this BEFORE installing v3.1 if you want a clean slate.
# This removes old v2 files that might conflict.
#
# WARNING: Creates backup first, but review before running.

param(
    [string]$AppDir = "C:\Users\james\novel_assistant",
    [switch]$Force = $false
)

Write-Host "=== Novel Assistant Cleanup Script ===" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $AppDir)) {
    Write-Host "Application directory not found: $AppDir" -ForegroundColor Red
    exit 1
}

# Files/folders to remove (old v2 structure)
$ItemsToRemove = @(
    # Old research structure
    "research/digests/historical",
    "research/digests/locations", 
    "research/digests/characters",
    "research/digests/themes",
    "research/digests/style",
    
    # Old service files
    "services/research_ingest.py",
    "services/research_digestor.py",
    "services/research_reviewer.py",
    "services/enhanced_reference_loader.py",
    "services/proactive_suggestions.py",
    
    # Old reference files
    "reference/literary_voice_guide.md",
    "reference/objects_symbols.md",
    "reference/consistency_rules.md"
)

if (-not $Force) {
    Write-Host "The following items will be removed:" -ForegroundColor Yellow
    foreach ($item in $ItemsToRemove) {
        $path = Join-Path $AppDir $item
        if (Test-Path $path) {
            Write-Host "  $item" -ForegroundColor Gray
        }
    }
    Write-Host ""
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y') {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Create backup first
$BackupDir = Join-Path $AppDir "backup_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host ""
Write-Host "Creating backup at: $BackupDir" -ForegroundColor Green

foreach ($item in $ItemsToRemove) {
    $sourcePath = Join-Path $AppDir $item
    if (Test-Path $sourcePath) {
        $backupPath = Join-Path $BackupDir $item
        $backupParent = Split-Path $backupPath -Parent
        if (-not (Test-Path $backupParent)) {
            New-Item -ItemType Directory -Path $backupParent -Force | Out-Null
        }
        Copy-Item -Path $sourcePath -Destination $backupPath -Recurse -Force
    }
}

# Now remove
Write-Host ""
Write-Host "Removing old files..." -ForegroundColor Green

foreach ($item in $ItemsToRemove) {
    $path = Join-Path $AppDir $item
    if (Test-Path $path) {
        Write-Host "  Removing $item" -ForegroundColor Gray
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "=== Cleanup Complete ===" -ForegroundColor Green
Write-Host "Backup saved to: $BackupDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Now run install_v3.ps1 to install the new version." -ForegroundColor White
