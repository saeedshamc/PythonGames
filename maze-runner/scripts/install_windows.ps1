# Maze Runner Windows Installer Script
# This script installs the Maze Runner game on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Maze Runner Game Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking for Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Check Python version (need 3.8+)
Write-Host "Checking Python version..." -ForegroundColor Yellow
$versionOutput = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$version = [version]$versionOutput
if ($version -lt [version]"3.8") {
    Write-Host "ERROR: Python 3.8 or higher is required (found $version)" -ForegroundColor Red
    exit 1
}
Write-Host "Python version OK: $version" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
try {
    python -m venv venv
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create desktop shortcut
Write-Host ""
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\Maze Runner.lnk"
$targetPath = "$PWD\run.py"
$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "python"
$shortcut.Arguments = "`"$targetPath`""
$shortcut.WorkingDirectory = $PWD
$shortcut.Description = "Maze Runner Game"
$shortcut.Save()

# Create start menu entry
Write-Host "Creating Start Menu entry..." -ForegroundColor Yellow
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Maze Runner.lnk"
$shortcut = $wshShell.CreateShortcut($startMenuPath)
$shortcut.TargetPath = "python"
$shortcut.Arguments = "`"$targetPath`""
$shortcut.WorkingDirectory = $PWD
$shortcut.Description = "Maze Runner Game"
$shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the game:" -ForegroundColor Yellow
Write-Host "  1. Double-click the desktop shortcut" -ForegroundColor White
Write-Host "  2. Or run: python run.py" -ForegroundColor White
Write-Host "  3. Or activate venv and run: .\venv\Scripts\activate && python run.py" -ForegroundColor White
Write-Host ""
Write-Host "Game data will be saved in: ~\.maze_runner\" -ForegroundColor Cyan
Write-Host ""
