"""
Build script to create executable for Maze Runner game
"""
import subprocess
import sys
import os
import platform

def build_exe():
    """Build executable using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create single executable
        "--windowed",  # Hide console window
        "--name=MazeRunner",  # Name of executable
        "--hidden-import=pygame",
        "--hidden-import=numpy",
        "run.py"
    ]
    
    # Add data files based on platform
    if platform.system() == "Windows":
        cmd.extend(["--add-data", "src/maze_runner;src/maze_runner"])
    else:
        cmd.extend(["--add-data", "src/maze_runner:src/maze_runner"])
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        if platform.system() == "Windows":
            print("Executable location: dist/MazeRunner.exe")
        else:
            print("Executable location: dist/MazeRunner")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
