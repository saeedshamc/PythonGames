#!/bin/bash
# Maze Runner Portable Linux Builder
# This script creates a portable Linux version of the game

echo "========================================"
echo "  Building Portable Linux Version"
echo "========================================"
echo ""

# Check if Python is installed
echo "Checking for Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Found: Python $PYTHON_VERSION"

# Create portable directory
PORTABLE_DIR="MazeRunner_Portable_Linux"
if [ -d "$PORTABLE_DIR" ]; then
    rm -rf "$PORTABLE_DIR"
fi
mkdir -p "$PORTABLE_DIR"

# Copy game files
echo "Copying game files..."
cp -r src "$PORTABLE_DIR/"
cp run.py "$PORTABLE_DIR/"
cp requirements.txt "$PORTABLE_DIR/"

# Create portable Python environment
echo "Creating portable Python environment..."
python3 -m venv "$PORTABLE_DIR/python_env"

# Activate portable environment and install dependencies
echo "Installing dependencies..."
source "$PORTABLE_DIR/python_env/bin/activate"
pip install --upgrade pip
pip install -r "$PORTABLE_DIR/requirements.txt"
deactivate

# Create launcher script
echo "Creating launcher script..."
cat > "$PORTABLE_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source python_env/bin/activate
python run.py
EOF
chmod +x "$PORTABLE_DIR/start.sh"

# Create README for portable version
cat > "$PORTABLE_DIR/README.txt" << 'EOF'
# Maze Runner - Portable Linux Version

## How to Run
1. Open terminal and navigate to this directory
2. Run: ./start.sh
3. Or double-click start.sh (if executable permissions are set)

## Game Data
Your progress and saved levels are stored in:
~/.maze_runner/

## Requirements
- Linux with glibc 2.17 or higher
- No additional installation required (Python included)

## Controls
- Arrow Keys or WASD: Move
- Q: Return to menu
- ESC: Quit game
- C: Clear progress (in menu)
EOF

# Create tar.gz archive
echo "Creating tar.gz archive..."
TAR_FILE="$PORTABLE_DIR.tar.gz"
if [ -f "$TAR_FILE" ]; then
    rm "$TAR_FILE"
fi
tar -czf "$TAR_FILE" "$PORTABLE_DIR"

echo ""
echo "========================================"
echo "  Portable Build Complete!"
echo "========================================"
echo ""
echo "Portable version: $PORTABLE_DIR"
echo "Archive: $TAR_FILE"
echo ""
