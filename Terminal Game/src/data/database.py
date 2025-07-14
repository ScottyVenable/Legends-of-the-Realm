"""
Game data management and loading utilities.
"""
import os
import json
from colorama import Fore


class GameData:
    def __init__(self):
        """Initialize and load all game data from JSON files."""
        # Determine the correct data path (assets/data for new structure)
        self.data_path = self._get_data_path()
        
        self.items = self.load_data(os.path.join(self.data_path, "items.json"))
        self.npcs = self.load_data(os.path.join(self.data_path, "npcs.json"))
        self.enemies = self.load_data(os.path.join(self.data_path, "enemies.json"))
        self.quests = self.load_data(os.path.join(self.data_path, "quests.json"))
        self.locations = self.load_data(os.path.join(self.data_path, "locations.json"))
        self.races = self.load_data(os.path.join(self.data_path, "races.json"))
        self.backgrounds = self.load_data(os.path.join(self.data_path, "backgrounds.json"))
        self.classes = self.load_data(os.path.join(self.data_path, "classes.json"))
        self.game_info = self.load_data(os.path.join(self.data_path, "gameinfo.json"))
        self.shops = self.load_data(os.path.join(self.data_path, "shops.json"))
        self.dialogue = self.load_data(os.path.join(self.data_path, "dialogues.json"))
        
        # Load settings from config directory
        self.settings = self.load_data(os.path.join(self._get_config_path(), "settings.json"))

        # Game metadata
        self.title = self.game_info.get('Name', 'Game Title')
        self.version = self.game_info.get('Version', '1.0')
        self.year = self.game_info.get('CopyrightYear', '2023')
        self.publisher = self.game_info.get('Publisher', 'Game Publisher')
        self.developer = self.game_info.get('Developer', 'Game Developer')

        # Developer settings
        self.DeveloperModeEnabled = self.settings.get('Developer Mode', False)
        self.DevDataDisplayAtStartup = self.settings.get('Developer Data Display At Startup', False)

    def _get_data_path(self):
        """Get the correct path to data files."""
        # Check if we're in the new structure
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        assets_data_path = os.path.join(current_dir, "assets", "data")
        
        if os.path.exists(assets_data_path):
            return assets_data_path
        else:
            # Fall back to old structure
            return os.path.join(current_dir, "data")
    
    def _get_config_path(self):
        """Get the correct path to config files."""
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(current_dir, "config")
        
        if os.path.exists(config_path):
            return config_path
        else:
            # Fall back to root directory
            return current_dir

    def load_data(self, filename):
        """Load data from a JSON file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                return data
            else:
                print(Fore.RED + f"Error: Could not find {filename}. Using empty data.")
                return {}
        except FileNotFoundError:
            print(Fore.RED + f"Error: Could not find {filename}")
            return {}
        except json.JSONDecodeError as e:
            print(Fore.RED + f"Error: Could not parse {filename}: {e}")
            return {}
