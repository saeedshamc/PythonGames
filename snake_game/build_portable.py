"""
Build script to create a portable version of the Snake Game.
This script uses PyInstaller to create a standalone executable.
"""

import os
import sys
import subprocess
import shutil

def build_portable():
    """Build a portable executable using PyInstaller."""
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # Hide console window (remove this if you want to see console)
        "--name", "SnakeGame",  # Name of the executable
        "--icon=NONE",  # Add icon file if you have one
        "--add-data", "Readme.md:.",  # Include README
        "--clean",  # Clean before building
        "snake_game.py"
    ]
    
    print("Building portable executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ Portable executable created successfully!")
        print(f"Executable location: dist/SnakeGame.exe")
        
        # Create a portable package folder
        portable_dir = "portable"
        if os.path.exists(portable_dir):
            shutil.rmtree(portable_dir)
        
        os.makedirs(portable_dir)
        
        # Copy executable
        shutil.copy("dist/SnakeGame.exe", portable_dir)
        
        # Copy README
        if os.path.exists("Readme.md"):
            shutil.copy("Readme.md", portable_dir)
        
        # Create a batch file to run the game
        with open(os.path.join(portable_dir, "run.bat"), "w") as f:
            f.write("@echo off\n")
            f.write("echo Starting Snake Game...\n")
            f.write("SnakeGame.exe\n")
            f.write("pause\n")
        
        print(f"\n✓ Portable package created in '{portable_dir}' folder")
        print("You can now distribute this folder as a portable version.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error building executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_portable()
