"""
Legends of the Realm - Main entry point for the game.

A text-based RPG adventure game with shops, battles, character creation, and exploration.
"""
import os
import time
import sys
from colorama import Fore, init

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.game import Game
from src.data.database import GameData
from src.ui.display import clear_console

try:
    from prettytable import PrettyTable, DOUBLE_BORDER
except ImportError:
    from src.utils.tools import PrettyTable, DOUBLE_BORDER

# Initialize colorama for colored output
init(autoreset=True)


def main():
    """Main function to start the game."""
    try:
        # Load game data
        game_data = GameData()
        game_instance = Game()
        
        # Check if developer mode is enabled for data display
        if game_data.DevDataDisplayAtStartup:
            clear_console()
            print(Fore.CYAN + f"Developer mode: {Fore.GREEN}ENABLED{Fore.RESET}")
            print(Fore.CYAN + f"Loading data...{Fore.RESET}\n\n")
            time.sleep(2)

            if PrettyTable:
                npc_names = []
                npc_roles = []
                npc_types = []
                npc_locations = []

                # Add all the NPC data to their categories Names, Roles, Locations
                for npc_data in game_data.npcs:
                    npc = game_data.npcs[npc_data]
                    npc_names.append(f"{Fore.BLUE}{npc['name']}{Fore.RESET}")
                    npc_roles.append(f"{Fore.LIGHTRED_EX}{npc['role']}{Fore.RESET}")
                    npc_types.append(f"{Fore.LIGHTYELLOW_EX}{npc['type']}{Fore.RESET}")
                    npc_locations.append(f"{Fore.GREEN}{npc['locations']}{Fore.RESET}")

                npc_table = PrettyTable()
                if hasattr(npc_table, 'title'):
                    npc_table.title = f"{Fore.YELLOW}NPCs{Fore.RESET}"
                if hasattr(npc_table, 'border'):
                    npc_table.border = True
                if hasattr(npc_table, 'add_column'):
                    npc_table.add_column("Name", npc_names)
                    npc_table.add_column("Type", npc_types)
                    npc_table.add_column("Role", npc_roles)
                    npc_table.add_column("Location", npc_locations)
                else:
                    npc_table.field_names = ["Name", "Type", "Role", "Location"]
                    for i in range(len(npc_names)):
                        npc_table.add_row([npc_names[i], npc_types[i], npc_roles[i], npc_locations[i]])

                if hasattr(npc_table, 'set_style') and DOUBLE_BORDER:
                    npc_table.set_style(DOUBLE_BORDER)
                if hasattr(npc_table, 'align'):
                    npc_table.align = "l"
                if hasattr(npc_table, 'sortby'):
                    npc_table.sortby = "Type"

                print(npc_table)
                input(f"{Fore.YELLOW}\nPress any key to continue...")
        
        # Start the game
        game_instance.game(game_data)
        
    except KeyboardInterrupt:
        print(Fore.RED + "\nGame exited.")
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
