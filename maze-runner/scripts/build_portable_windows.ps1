# Maze Runner Portable Windows Builder
# This script creates a portable Windows version of the game

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Building Portable Windows Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking for Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed" -ForegroundColor Red
    exit 1
}

# Create portable directory
$portableDir = "MazeRunner_Portable_Windows"
if (Test-Path $portableDir) {
    Remove-Item -Recurse -Force $portableDir
}
New-Item -ItemType Directory -Path $portableDir | Out-Null

# Copy game files
Write-Host "Copying game files..." -ForegroundColor Yellow
Copy-Item -Recurse -Force "src" "$portableDir\src"
Copy-Item -Force "run.py" "$portableDir\"
Copy-Item -Force "requirements.txt" "$portableDir\"

# Create portable Python environment
Write-Host "Creating portable Python environment..." -ForegroundColor Yellow
python -m venv "$portableDir\python_env"

# Activate portable environment and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& "$portableDir\python_env\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r "$portableDir\requirements.txt"

# Create launcher script
Write-Host "Creating launcher script..." -ForegroundColor Yellow
$launcherContent = @"
@echo off
cd /d "%~dp0"
call python_env\Scripts\activate.bat
python run.py
pause
"@
Set-Content -Path "$portableDir\Start.bat" -Value $launcherContent

# Create README for portable version
$readmeContent = @"
# Maze Runner - Portable Windows Version

## How to Run
1. Double-click `Start.bat` to launch the game
2. The game will start in a new window

## Game Data
Your progress and saved levels are stored in:
`%USERPROFILE%\.maze_runner\`

## Requirements
- Windows 10 or later
- No additional installation required (Python included)

## Controls
- Arrow Keys or WASD: Move
- Q: Return to menu
- ESC: Quit game
- C: Clear progress (in menu)
"@
Set-Content -Path "$portableDir\README.txt" -Value $readmeContent

# Create ZIP archive
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$zipFile = "$portableDir.zip"
if (Test-Path $zipFile) {
    Remove-Item -Force $zipFile
}
Compress-Archive -Path $portableDir -DestinationPath $zipFile

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Portable Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Portable version: $portableDir" -ForegroundColor White
Write-Host "ZIP archive: $zipFile" -ForegroundColor White
Write-Host ""
