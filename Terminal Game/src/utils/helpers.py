"""
Utility functions for save/load game functionality.
"""
import os
import json
from colorama import Fore
from ..ui.display import clear_console


def save_game(player):
    """Save the current game state."""
    save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'savegame.json')
    
    with open(save_path, 'w') as f:
        json.dump(player.__dict__, f)
    print(Fore.GREEN + "Game saved successfully!")
    input("Press Enter to continue...")


def load_game():
    """Load a saved game state."""
    save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves', 'savegame.json')
    
    if os.path.exists(save_path):
        with open(save_path, 'r') as f:
            data = json.load(f)
        
        # Import here to avoid circular imports
        from ..entities.character import Character
        
        player = Character("", "", "", "", "")
        player.__dict__.update(data)
        clear_console()
        print(Fore.GREEN + "Game loaded successfully!")
        input("Press Enter to play...")
        return player
    else:
        print(Fore.RED + "No saved game found.")
        input("Press Enter to continue...")
        return None
