"""
Menu system and user input handling.
"""
import time
from colorama import Fore
from .display import clear_console

try:
    import keyboard
except ImportError:
    print("keyboard not installed. Install with: pip install keyboard")
    # Create fallback keyboard module
    class FallbackKeyboard:
        @staticmethod
        def is_pressed(key):
            return False
    keyboard = FallbackKeyboard


def select_option(options, title="Select an option:", color=Fore.YELLOW, clear_screen=True, player_send=None, back_option=False):
    """
    Display a menu and handle user selection.
    
    Args:
        options: List of menu options
        title: Menu title
        color: Color for the title
        clear_screen: Whether to clear screen before showing menu
        player_send: Player object for inventory commands
        back_option: Whether to add a "Back" option
        
    Returns:
        tuple: (selected_option, index)
    """
    player = player_send
    while True:
        if clear_screen:
            clear_console()
        print(color + title)
        options_list = options
        if back_option:
            options_list.append("Back")
        for idx, option in enumerate(options_list):
            print(f"{idx + 1}. {option}")
        choice = input(f"\n{Fore.YELLOW} >>{Fore.CYAN} ")
        
        if keyboard.is_pressed('i'):  # Check if "i" is pressed
            if player:
                player.show_inventory_table()
                time.sleep(0.1)  # Add a slight delay to prevent multiple presses
        
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                if clear_screen:
                    clear_console()
                return options[index], index
            else:
                print(Fore.RED + "Invalid choice. Please select a valid option.\n")
                time.sleep(1)
                input(f"{Fore.BLUE}Press any key to continue...")
        elif choice.startswith("/"):
            if player is not None:
                from ..core.game import Game
                Game.parse_command(choice, player_send=player)
            else:
                print(Fore.RED + "Invalid code. No player identified!")
                time.sleep(1)
        else:
            print(Fore.RED + "Invalid input. Please enter a number.\n")
            time.sleep(1)
