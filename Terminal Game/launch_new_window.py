#!/usr/bin/env python3
"""
Simple launcher that opens the game in a new PowerShell window
"""
import subprocess
import os
import sys

def launch_in_new_window():
    """Launch the game in a new PowerShell window"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_path = os.path.join(script_dir, "game.py")
    
    # Command to run in a new PowerShell window
    cmd = [
        "powershell",
        "-NoExit", 
        "-Command", 
        f"cd '{script_dir}'; python '{game_path}'"
    ]
    
    try:
        print("Opening game in new PowerShell window...")
        subprocess.Popen(cmd, shell=True)
        print("Game window opened!")
    except Exception as e:
        print(f"Error opening new window: {e}")
        print("Falling back to current terminal...")
        os.system(f"python \"{game_path}\"")

if __name__ == "__main__":
    launch_in_new_window()
