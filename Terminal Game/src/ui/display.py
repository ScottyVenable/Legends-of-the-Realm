"""
Display utilities and console management for the game.
"""
import os
from colorama import Fore


def clear_console():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_titlebar(title, color=Fore.CYAN, border_char="="):
    """Print a formatted title bar."""
    terminal_width = 80  # Default width
    try:
        terminal_width = os.get_terminal_size().columns
    except:
        pass
    
    title_len = len(title)
    border_len = max(10, min(terminal_width - 4, 80))
    
    if title_len + 4 > border_len:
        border_len = title_len + 4
    
    padding = (border_len - title_len - 2) // 2
    
    print(color + border_char * border_len)
    print(border_char + " " * padding + title + " " * (border_len - title_len - padding - 2) + border_char)
    print(border_char * border_len)
