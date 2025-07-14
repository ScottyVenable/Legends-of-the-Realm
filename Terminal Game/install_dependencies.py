#!/usr/bin/env python3
import subprocess
import sys

def install_dependencies():
    """Install the required dependencies for the game."""
    dependencies = [
        "colorama>=0.4.4",
        "pygame>=2.0.0", 
        "prettytable>=3.0.0",
        "tabulate>=0.9.0",
        "keyboard>=0.13.0"
    ]
    
    print("Installing required dependencies...")
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
    
    print("\nDependencies installation complete!")
    print("You can now run the game with: python game.py")

if __name__ == "__main__":
    install_dependencies()
