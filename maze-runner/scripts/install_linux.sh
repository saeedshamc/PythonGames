#!/bin/bash
# Maze Runner Linux Installer Script
# This script installs the Maze Runner game on Linux

echo "========================================"
echo "  Maze Runner Game Installer"
echo "========================================"
echo ""

# Check if Python is installed
echo "Checking for Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  Fedora: sudo dnf install python3"
    echo "  Arch: sudo pacman -S python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Found: Python $PYTHON_VERSION"

# Check Python version (need 3.8+)
echo "Checking Python version..."
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 8 ]; then
    echo "ERROR: Python 3.8 or higher is required (found $PYTHON_MAJOR.$PYTHON_MINOR)"
    exit 1
fi
echo "Python version OK: $PYTHON_MAJOR.$PYTHON_MINOR"

# Check if pip is installed
echo "Checking for pip..."
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install pip"
        echo "Please install pip manually:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-pip"
        echo "  Fedora: sudo dnf install python3-pip"
        exit 1
    fi
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    echo "Please install python3-venv:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-venv"
    exit 1
fi
echo "Virtual environment created successfully"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"

# Create desktop entry
echo ""
echo "Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/maze-runner.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Maze Runner
Comment=Infinite maze exploration game
Exec=bash -c "cd $(pwd) && source venv/bin/activate && python run.py"
Icon=$(pwd)/icon.png
Terminal=false
Categories=Game;
EOF

# Create launcher script
echo "Creating launcher script..."
LAUNCHER_SCRIPT="$HOME/.local/bin/maze-runner"
mkdir -p "$HOME/.local/bin"
cat > "$LAUNCHER_SCRIPT" << EOF
#!/bin/bash
cd "$(pwd)"
source venv/bin/activate
python run.py
EOF
chmod +x "$LAUNCHER_SCRIPT"

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "To run the game:"
echo "  1. From applications menu (Maze Runner)"
echo "  2. Or run: $LAUNCHER_SCRIPT"
echo "  3. Or manually: cd $(pwd) && source venv/bin/activate && python run.py"
echo ""
echo "Game data will be saved in: ~/.maze_runner/"
echo ""
