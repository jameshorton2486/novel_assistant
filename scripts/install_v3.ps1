# Novel Assistant v3.1 Installation Script (Windows PowerShell)
# ============================================================
#
# This script:
# 1. Backs up your existing installation
# 2. Removes old files that conflict
# 3. Copies new v3.1 files to your application
#
# USAGE:
# 1. Download novel_assistant_v3.zip
# 2. Open PowerShell as Administrator
# 3. Run: .\install_v3.ps1

param(
    [string]$AppDir = "C:\Users\james\novel_assistant",
    [string]$DownloadDir = "$env:USERPROFILE\Downloads"
)

Write-Host "=== Novel Assistant v3.1 Installation ===" -ForegroundColor Cyan
Write-Host ""

# Verify paths
$ZipPath = Join-Path $DownloadDir "novel_assistant_v3.zip"
if (-not (Test-Path $ZipPath)) {
    Write-Host "ERROR: Cannot find $ZipPath" -ForegroundColor Red
    Write-Host "Please download novel_assistant_v3.zip first." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $AppDir)) {
    Write-Host "Creating application directory: $AppDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $AppDir -Force | Out-Null
}

# Step 1: Backup existing installation
Write-Host ""
Write-Host "Step 1: Creating backup..." -ForegroundColor Green
$BackupDir = Join-Path $AppDir "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$ItemsToBackup = @("services", "reference", "research", "docs")

foreach ($item in $ItemsToBackup) {
    $itemPath = Join-Path $AppDir $item
    if (Test-Path $itemPath) {
        $backupPath = Join-Path $BackupDir $item
        Write-Host "  Backing up $item..." -ForegroundColor Gray
        Copy-Item -Path $itemPath -Destination $backupPath -Recurse -Force
    }
}
Write-Host "  Backup created at: $BackupDir" -ForegroundColor Gray

# Step 2: Remove conflicting old files
Write-Host ""
Write-Host "Step 2: Removing old conflicting files..." -ForegroundColor Green

$OldFilesToRemove = @(
    "services/research_ingest.py",
    "services/research_digestor.py",
    "services/research_reviewer.py",
    "services/enhanced_reference_loader.py",
    "services/proactive_suggestions.py",
    "reference/literary_voice_guide.md"
)

foreach ($file in $OldFilesToRemove) {
    $filePath = Join-Path $AppDir $file
    if (Test-Path $filePath) {
        Write-Host "  Removing $file..." -ForegroundColor Gray
        Remove-Item $filePath -Force
    }
}

# Remove old digest structure if present
$OldDigestDir = Join-Path $AppDir "research\digests\historical"
if (Test-Path $OldDigestDir) {
    Write-Host "  Removing old digest structure..." -ForegroundColor Gray
    Remove-Item (Join-Path $AppDir "research\digests") -Recurse -Force -ErrorAction SilentlyContinue
}

# Step 3: Extract new files
Write-Host ""
Write-Host "Step 3: Extracting v3.1 files..." -ForegroundColor Green
$ExtractDir = Join-Path $DownloadDir "novel_assistant_v3_extract"

if (Test-Path $ExtractDir) {
    Remove-Item $ExtractDir -Recurse -Force
}

Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir -Force

# Step 4: Copy new files
Write-Host ""
Write-Host "Step 4: Installing new files..." -ForegroundColor Green

$SourceDir = Join-Path $ExtractDir "novel_assistant_v3"

# Copy services
$ServicesSource = Join-Path $SourceDir "services"
$ServicesDest = Join-Path $AppDir "services"
if (Test-Path $ServicesSource) {
    Write-Host "  Installing services..." -ForegroundColor Gray
    if (-not (Test-Path $ServicesDest)) {
        New-Item -ItemType Directory -Path $ServicesDest -Force | Out-Null
    }
    Copy-Item -Path "$ServicesSource\*" -Destination $ServicesDest -Recurse -Force
}

# Copy governance
$GovSource = Join-Path $SourceDir "governance"
$GovDest = Join-Path $AppDir "governance"
if (Test-Path $GovSource) {
    Write-Host "  Installing governance..." -ForegroundColor Gray
    if (-not (Test-Path $GovDest)) {
        New-Item -ItemType Directory -Path $GovDest -Force | Out-Null
    }
    Copy-Item -Path "$GovSource\*" -Destination $GovDest -Recurse -Force
}

# Copy models
$ModelsSource = Join-Path $SourceDir "models"
$ModelsDest = Join-Path $AppDir "models"
if (Test-Path $ModelsSource) {
    Write-Host "  Installing models..." -ForegroundColor Gray
    if (-not (Test-Path $ModelsDest)) {
        New-Item -ItemType Directory -Path $ModelsDest -Force | Out-Null
    }
    Copy-Item -Path "$ModelsSource\*" -Destination $ModelsDest -Recurse -Force
}

# Copy reference
$RefSource = Join-Path $SourceDir "reference"
$RefDest = Join-Path $AppDir "reference"
if (Test-Path $RefSource) {
    Write-Host "  Installing reference files..." -ForegroundColor Gray
    if (-not (Test-Path $RefDest)) {
        New-Item -ItemType Directory -Path $RefDest -Force | Out-Null
    }
    Copy-Item -Path "$RefSource\*" -Destination $RefDest -Recurse -Force
}

# Copy research structure (empty directories)
$ResearchDirs = @(
    "research/intake",
    "research/context",
    "research/artifacts",
    "research/craft",
    "research/canon_staging",
    "research/rejected"
)

foreach ($dir in $ResearchDirs) {
    $dirPath = Join-Path $AppDir $dir
    if (-not (Test-Path $dirPath)) {
        Write-Host "  Creating $dir..." -ForegroundColor Gray
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}

# Copy docs
$DocsSource = Join-Path $SourceDir "docs"
$DocsDest = Join-Path $AppDir "docs"
if (Test-Path $DocsSource) {
    Write-Host "  Installing documentation..." -ForegroundColor Gray
    if (-not (Test-Path $DocsDest)) {
        New-Item -ItemType Directory -Path $DocsDest -Force | Out-Null
    }
    Copy-Item -Path "$DocsSource\*" -Destination $DocsDest -Recurse -Force
}

# Ensure other directories exist
$RequiredDirs = @("chapters", "exports", "reports")
foreach ($dir in $RequiredDirs) {
    $dirPath = Join-Path $AppDir $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}

# Cleanup
Write-Host ""
Write-Host "Step 5: Cleaning up..." -ForegroundColor Green
Remove-Item $ExtractDir -Recurse -Force

# Done
Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installed components:" -ForegroundColor White
Write-Host "  - Research governance system (4-class model)" -ForegroundColor Gray
Write-Host "  - Reference loader with context awareness" -ForegroundColor Gray
Write-Host "  - Canon versioning and changelog" -ForegroundColor Gray
Write-Host "  - Chapter locking (Draft/Revised/Locked/Published)" -ForegroundColor Gray
Write-Host "  - Era language linter (1950s enforcement)" -ForegroundColor Gray
Write-Host "  - Multi-model router (Claude/GPT/Gemini)" -ForegroundColor Gray
Write-Host "  - Advisory mode with governance" -ForegroundColor Gray
Write-Host "  - Google Drive sync" -ForegroundColor Gray
Write-Host "  - Export pipeline (DOCX/EPUB)" -ForegroundColor Gray
Write-Host ""
Write-Host "Directory structure:" -ForegroundColor White
Write-Host "  $AppDir" -ForegroundColor Gray
Write-Host "  ├── services/        (core Python modules)" -ForegroundColor Gray
Write-Host "  ├── governance/      (canon + chapter locking)" -ForegroundColor Gray
Write-Host "  ├── models/          (multi-model router)" -ForegroundColor Gray
Write-Host "  ├── reference/       (CANON - sacred)" -ForegroundColor Gray
Write-Host "  ├── research/" -ForegroundColor Gray
Write-Host "  │   ├── intake/      (upload queue)" -ForegroundColor Gray
Write-Host "  │   ├── context/     (background)" -ForegroundColor Gray
Write-Host "  │   ├── artifacts/   (scene triggers)" -ForegroundColor Gray
Write-Host "  │   └── craft/       (writing guidance)" -ForegroundColor Gray
Write-Host "  ├── chapters/        (manuscript)" -ForegroundColor Gray
Write-Host "  └── exports/         (output files)" -ForegroundColor Gray
Write-Host ""
Write-Host "Backup saved to: $BackupDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review docs/OPERATIONAL_GUIDE.md" -ForegroundColor Gray
Write-Host "  2. Upload research documents to intake/" -ForegroundColor Gray
Write-Host "  3. Run the application: python main.py" -ForegroundColor Gray
