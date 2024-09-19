from enum import Enum
import random
import shutil
import time
import os
import json
from colorama import init, Fore, Style
import pygame
import threading
import sys
from tabulate import tabulate
from prettytable import PrettyTable, MARKDOWN, SINGLE_BORDER, DOUBLE_BORDER, DEFAULT, PLAIN_COLUMNS, MSWORD_FRIENDLY, FRAME, RANDOM

# Initialize colorama
init(autoreset=True)
# Utility Functions
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_option(options, title="Select an option:", color=Fore.YELLOW, clear_screen=True, player_send=None):
    player = player_send
    while True:
        if clear_screen:
            clear_console()
        print(color + title)
        for idx, option in enumerate(options):
            print(f"{idx + 1}. {option}")
        choice = input(f"\n{Fore.YELLOW}Enter the number of your choice:{Fore.CYAN} ")
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
            if player != None:
                Game.parse_command(choice, player_send=player)
            else:
                print(Fore.RED + "Invalid code. No player identified!")
                time.sleep(1)
        else:
            print(Fore.RED + "Invalid input. Please enter a number.\n")
            time.sleep(1)

def save_game(player):
    with open('savegame.json', 'w') as f:
        json.dump(player.__dict__, f)
    print(Fore.GREEN + "Game saved successfully!")
    input("Press Enter to continue...")

def load_game():
    if os.path.exists('savegame.json'):
        with open('savegame.json', 'r') as f:
            data = json.load(f)
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

# Game Data
class GameData:
    def __init__(self):
        self.items = self.load_data(os.path.join("data", "items.json"))
        self.npcs = self.load_data(os.path.join("data", "npcs.json"))
        self.enemies = self.load_data(os.path.join("data", "enemies.json"))
        self.quests = self.load_data(os.path.join("data", "quests.json"))
        self.locations = self.load_data(os.path.join("data", "locations.json"))
        self.races = self.load_data(os.path.join("data", "races.json"))
        self.backgrounds = self.load_data(os.path.join("data", "backgrounds.json"))
        self.classes = self.load_data(os.path.join("data", "classes.json"))
        self.game_info = self.load_data(os.path.join("data", "gameinfo.json"))
        self.settings = self.load_data("settings.json")
        self.shops = self.load_data(os.path.join("data", "shops.json"))
        self.dialogue = self.load_data(os.path.join("data", "dialogues.json"))

        self.title = self.game_info.get('Name', 'Game Title')
        self.version = self.game_info.get('Version', '1.0')
        self.year = self.game_info.get('CopyrightYear', '2023')
        self.publisher = self.game_info.get('Publisher', 'Game Publisher')
        self.developer = self.game_info.get('Developer', 'Game Developer')
        self.DeveloperModeEnabled = self.settings.get('Developer Mode', False)

    def load_data(self, filename):
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
        


# Character Classes
class Character:
    def __init__(self, name, race, gender, background, char_class):
        self.name = name
        self.race = race
        self.gender = gender
        self.background = background
        self.char_class = char_class
        self.level = 1
        self.exp = 0
        self.inventory = []
        self.abilities = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.gold = 10  # Will be adjusted based on background
        self.relationships = {}
        self.location = 'Village'
        self.attributes = {}  # Will be set in character creation
        self.modifiers = {}
        self.proficiencies = []
        self.skills = self.initialize_skills()
        self.set_class_attributes()
        self.set_background_attributes()
        self.health = 0
        self.max_health = 0
        self.ac = 10

    def roll_attributes(self):
        attributes = {}
        for attr in ['Strength', 'Dexterity', 'Fortitude', 'Intelligence', 'Wisdom', 'Charisma']:
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            attributes[attr] = sum(rolls)
        return attributes
    
    def get_ac(self):
        self.ac = 10 + self.modifiers['Dexterity']
        if self.equipped_armor:
            self.ac += self.equipped_armor.get('ac_bonus', 0)
        return self.ac

    def point_buy_attributes(self):
        attributes = {'Strength': 8, 'Dexterity': 8, 'Fortitude': 8,
                      'Intelligence': 8, 'Wisdom': 8, 'Charisma': 8}
        points = 27
        while points > 0:
            clear_console()
            print(Fore.YELLOW + f"You have {points} points to spend.")
            for attr, score in attributes.items():
                mod = (score - 10) // 2
                print(f"{attr}: {score} ({mod:+})")
            attr_choice, _ = select_option(list(attributes.keys()), "\nSelect an attribute to increase:", clear_screen=False)
            if attributes[attr_choice] < 15:
                cost = 1 if attributes[attr_choice] < 13 else 2
                if points >= cost:
                    attributes[attr_choice] += 1
                    points -= cost
                else:
                    print(Fore.RED + "Not enough points.")
                    time.sleep(1)
            else:
                print(Fore.RED + "Attribute cannot be increased further.")
                time.sleep(1)
        return attributes

    def update_modifiers(self):
        self.modifiers = {attr: (score - 10) // 2 for attr, score in self.attributes.items()}

    def initialize_skills(self):
        skills = {
            'Acrobatics': 'Dexterity',
            'Animal Handling': 'Wisdom',
            'Arcana': 'Intelligence',
            'Athletics': 'Strength',
            'Deception': 'Charisma',
            'History': 'Intelligence',
            'Insight': 'Wisdom',
            'Intimidation': 'Charisma',
            'Investigation': 'Intelligence',
            'Medicine': 'Wisdom',
            'Nature': 'Intelligence',
            'Perception': 'Wisdom',
            'Performance': 'Charisma',
            'Persuasion': 'Charisma',
            'Religion': 'Intelligence',
            'Sleight of Hand': 'Dexterity',
            'Stealth': 'Dexterity',
            'Survival': 'Wisdom',
        }
        return skills

    def set_class_attributes(self):
        class_hp = {
            'Fighter': 10,
            'Rogue': 8,
            'Wizard': 6,
            'Cleric': 8,
            'Ranger': 10,
        }
        class_proficiencies = {
            'Fighter': ['Athletics', 'Survival'],
            'Rogue': ['Stealth', 'Acrobatics'],
            'Wizard': ['Arcana', 'History'],
            'Cleric': ['Religion', 'Medicine'],
            'Ranger': ['Nature', 'Perception'],
        }
        self.class_hp = class_hp.get(self.char_class, 8)
        self.proficiencies.extend(class_proficiencies.get(self.char_class, []))
        self.abilities.extend(game_data.classes)

    def set_background_attributes(self):
        background_proficiencies = {
            'Noble': ['History', 'Persuasion'],
            'Soldier': ['Athletics', 'Intimidation'],
            'Scholar': ['Arcana', 'History'],
            'Criminal': ['Deception', 'Stealth'],
            'Hermit': ['Medicine', 'Religion'],
        }
        background_gold = {
            'Noble': random.randint(50, 100),
            'Soldier': random.randint(20, 50),
            'Scholar': random.randint(15, 40),
            'Criminal': random.randint(25, 60),
            'Hermit': random.randint(10, 30),
        }
        self.proficiencies.extend(background_proficiencies.get(self.background, []))
        self.gold = background_gold.get(self.background, 10)
        self.inventory.extend(self.get_starting_equipment())

    def get_starting_equipment(self):
        equipment = []
        if self.background == 'Noble':
            equipment.append({'name': 'Fine Clothes', 'type': 'armor', 'ac_bonus': 0})
        elif self.background == 'Soldier':
            equipment.append({'name': 'Shield', 'type': 'armor', 'ac_bonus': 2})
        elif self.background == 'Scholar':
            equipment.append({'name': 'Book of Lore', 'type': 'misc'})
        elif self.background == 'Criminal':
            equipment.append({'name': 'Lockpicks', 'type': 'tool'})
        elif self.background == 'Hermit':
            equipment.append({'name': 'Herbal Kit', 'type': 'tool'})
        # Class-specific equipment
        if self.char_class == 'Fighter':
            equipment.append({'name': 'Longsword', 'type': 'weapon', 'damage': '1d8', 'attack_bonus': 2})
            self.equipped_weapon = equipment[-1]
        elif self.char_class == 'Rogue':
            equipment.append({'name': 'Dagger', 'type': 'weapon', 'damage': '1d4', 'attack_bonus': 1})
            self.equipped_weapon = equipment[-1]
        elif self.char_class == 'Wizard':
            equipment.append({'name': 'Spellbook', 'type': 'misc'})
        elif self.char_class == 'Cleric':
            equipment.append({'name': 'Mace', 'type': 'weapon', 'damage': '1d6', 'attack_bonus': 1})
            self.equipped_weapon = equipment[-1]
        elif self.char_class == 'Ranger':
            equipment.append({'name': 'Bow', 'type': 'weapon', 'damage': '1d8', 'attack_bonus': 2})
            self.equipped_weapon = equipment[-1]
        return equipment

    def calculate_max_health(self):
        return self.class_hp + self.modifiers['Fortitude']

    def level_up(self):
        self.level += 1
        hp_increase = random.randint(1, self.class_hp) + self.modifiers['Fortitude']
        self.max_health += max(1, hp_increase)
        self.health = self.max_health
        print(Fore.YELLOW + f"\nYou have leveled up to Level {self.level}!")
        print(Fore.GREEN + f"Your maximum health increased by {max(1, hp_increase)}!")
        # Improve a skill or gain a new ability
        self.choose_skill_improvement()
        input("Press Enter to continue...")

    def choose_skill_improvement(self):
        print(Fore.CYAN + "\nChoose a skill to improve:")
        skill_choices = list(set(self.skills.keys()) - set(self.proficiencies))
        if not skill_choices:
            print("You have already mastered all skills!")
            return
        skill_choice, _ = select_option(skill_choices, clear_screen=False)
        self.proficiencies.append(skill_choice)
        print(Fore.GREEN + f"You have gained proficiency in {skill_choice}!")

    def adjust_health(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health < 0:
            self.health = 0


    def show_stats(self, clear=True):
        if clear:
            clear_console()
        print_titlebar("large", "CHARACTER SHEET", Fore.BLUE)
        print(Fore.YELLOW + f"\nName: {Fore.CYAN}{self.name}")
        print(Fore.YELLOW + f"Gender: {Fore.CYAN}{self.gender}")
        print(Fore.YELLOW + f"Race: {Fore.CYAN}{self.race}")
        print(Fore.YELLOW + f"Class: {Fore.CYAN}{self.char_class}")
        print(Fore.YELLOW + f"Background: {Fore.CYAN}{self.background}")
        print(Fore.YELLOW + f"Level: {self.level}")
        print(Fore.RED + f"Health: {self.health}/{self.max_health}")
        print(Fore.YELLOW + f"Armor Rating: {self.ac}")
        print(Fore.YELLOW + "\nAttributes:")
        for attr, score in self.attributes.items():
            mod = self.modifiers[attr]
            print(f"  {attr}: {score} ({mod:+})")
        print(Fore.MAGENTA + f"\nExperience: {self.exp}")
        print(Fore.YELLOW + f"Gold: {self.gold}")
        inventory_names = [item['name'] for item in self.inventory]
        print(Fore.MAGENTA + f"Inventory: {inventory_names}")
        if self.equipped_weapon:
            print(Fore.CYAN + f"Equipped Weapon: {self.equipped_weapon['name']}")
        if self.equipped_armor:
            print(Fore.CYAN + f"Equipped Armor: {self.equipped_armor['name']}")
        prof_str = ', '.join(set(self.proficiencies))
        print(Fore.CYAN + f"Proficiencies: {prof_str if prof_str else 'None'}")
        print(Fore.CYAN + f"Location: {self.location}")

    def equip_item(self, item):
        if item['type'] == 'weapon':
            self.equipped_weapon = item
            print(Fore.GREEN + f"You have equipped {item['name']}.")
        elif item['type'] == 'armor':
            self.equipped_armor = item
            self.ac += item.get('ac_bonus', 0)
            print(Fore.GREEN + f"You have equipped {item['name']}.")
        else:
            print(Fore.RED + f"You cannot equip {item['name']}.")

    def move_to_location(self, location_name, game_data):
        if location_name in game_data.locations:
            self.location = location_name
            location = game_data.locations[location_name]
            clear_console()

            # Todo -- Implement Travel Mechanic to wait to travel, etc.
            print(Fore.YELLOW + f"\nYou travel to {Fore.CYAN}{location['name']}{Fore.RESET}.")
            print(location.get('description', ''))
            input("Press Enter to continue...")
        else:
            print(Fore.RED + "That location does not exist.")

    def show_inventory_table(self):
        clear_console()  # Assuming you have this function defined
        print_titlebar("normal", "INVENTORY", Fore.YELLOW)  # Assuming you have this function defined

        if not self.inventory:
            print(Fore.RED + "Your inventory is empty.")
            input("\nPress Enter to continue...")
            return

        # Prepare data for the table
        inventory_data = []
        for idx, item in enumerate(self.inventory):
            item_type = item.get('type', 'Unknown')
            inventory_data.append([idx + 1, item['name'], str(item_type).upper()])

        # Create and print the table
        table = Tools.make_table(
            data=inventory_data,
            field_names=["#", "Item Name", "Type"],
            align="l",
            vrules=FRAME,
        )
        table.min_width = 1
        table.max_table_width = Tools.get(Tools.Values.CONSOLE_WIDTH) - 3
        table.min_table_width = 50
        table.set_style(DOUBLE_BORDER)
        print(table)

        # Get user input
        print(f"    {len(self.inventory) + 1}. {Fore.RED}Back{Fore.RESET}")
        choice = input("\nSelect an item to use or equip, or press the number for 'Back': ")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(self.inventory):
                selected_item = self.inventory[choice - 1]
                self.use_item(selected_item)  # Assuming you have this function defined
            else:
                return  # Go back
        else:
            print(Fore.RED + "Invalid input.")
            time.sleep(1)

    def use_item(self, item):
        if item['type'] == 'weapon' or item['type'] == 'armor':
            self.equip_item(item)
        elif item['type'] == 'consumable':
            effect = item.get('effect')
            if effect == 'heal':
                self.adjust_health(item.get('value', 0))
                self.inventory.remove(item)
                print(Fore.GREEN + f"You used {item['name']} and healed {item.get('value', 0)} health.")
        else:
            print(Fore.RED + f"You can't use {item['name']}.")
        input("\nPress Enter to continue.")

    def player_killed(player):
        if "Second Life" in player.abilities:
            print("")
        else:
            clear_console()
            Tools.is_music_playing = False
            Art.game_over(Fore.RED)
            time.sleep(2)
            Tools.is_music_playing = True
            music_thread = threading.Thread(target=play_music, args=(os.path.join("music", "game_over.mp3"),))
            music_thread.start()
            time.sleep(8)
            clear_console()
            choice = input("Would you like to continue? (Y/N): ")
            if choice.lower == "y":
                Game.game(GameData)
                is_music_playing = False
            else:
                clear_console()
                print("Thanks for playing!!\n")
                is_music_playing = True

                sys.exit()
        
        # Handle player defeat (e.g., game over, respawn)
        
class Dialogue:
    def __init__(self, text, responses=None, action=None, id=None, speaker=None, options=[]):
        self.text = text
        self.responses = responses if responses is not None else []
        self.action = action
        self.id = id
        self.speaker = speaker
        self.options = options

class Tools:
    is_music_playing = True
    class Values:
        CONSOLE_WIDTH = 0
        DIALOGUE_INTRO_GREETING = 0
        DIALOGUE_NORMAL_GREETING = 1

    def get(type):
        if type == Tools.Values.CONSOLE_WIDTH:
            console_width = shutil.get_terminal_size().columns
            return console_width
        
    def make_table(data, title="", field_names=None, align="l", style=SINGLE_BORDER, title_color=Fore.RESET, vrules=None, hrules=None, sortby=None, reversesort=False, min_width=10, max_width=20):
        """
        Creates a formatted table using PrettyTable.

        Args:
            title (str): The title of the table.
            data (list of lists or dict): The data to display in the table.
            field_names (list, optional): Column names for the table. If not provided,
                                        keys from the first item in data (if a dict)
                                        or range(len(data[0])) (if a list of lists)
                                        will be used.
            align (str, optional): Alignment for all columns ("l" for left, "r" for right, "c" for center).
            vrules (str, optional): Vertical rules style ("FRAME", "ALL", "NONE").
            hrules (str, optional): Horizontal rules style ("FRAME", "ALL", "NONE").
            sortby (str, optional): Column name to sort the table by.
            reversesort (bool, optional): Reverse the sorting order if True.

        Returns:
            PrettyTable: The formatted table object.
        """

        max_width = Tools.get(Tools.Values.CONSOLE_WIDTH) - 4
        table = PrettyTable()

        # Set column names
        if field_names:
            table.field_names = field_names
        elif isinstance(data, dict) and data:
            table.field_names = list(data.keys())
        elif isinstance(data, list) and data and isinstance(data[0], list):
            table.field_names = [str(i) for i in range(len(data[0]))]  # Default to numeric column names

        # Add rows
        if isinstance(data, dict):
            table.add_row(data.values())
        else:
            for row in data:
                table.add_row(row)

        # Apply formatting
        table.align = align
        if vrules:
            table.vrules = getattr(PrettyTable, vrules)
        if hrules:
            table.hrules = getattr(PrettyTable, hrules)
        if sortby:
            table.sortby = sortby
            table.reversesort = reversesort
        if title:
            table.title = f"{title_color}{title}{Fore.RESET}"
        if style:
            table.set_style(style)
        if max_width:
            table.max_width = max_width
        if min_width:
            table.min_width = min_width


        return table

    def tell_story(story_name, music="music.mp3", wait_speed=5, start_delay=1):
        if story_name == "creation":
            music_path = os.path.join("music", "the_creation.mp3")
            play_music(music_path)

            clear_console()
            time.sleep(start_delay)
            print(f"""{Fore.LIGHTCYAN_EX}
                  
            ████████╗██╗  ██╗███████╗     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
            ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
               ██║   ███████║█████╗      ██║     ██████╔╝█████╗  ███████║   ██║   ██║██║   ██║██╔██╗ ██║
               ██║   ██╔══██║██╔══╝      ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
               ██║   ██║  ██║███████╗    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
               ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
""")
            time.sleep(1)
            clear_console()
            print(f"""{Fore.CYAN}
                  
            ████████╗██╗  ██╗███████╗     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
            ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
               ██║   ███████║█████╗      ██║     ██████╔╝█████╗  ███████║   ██║   ██║██║   ██║██╔██╗ ██║
               ██║   ██╔══██║██╔══╝      ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
               ██║   ██║  ██║███████╗    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
               ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
""")
            time.sleep(1)
            clear_console()
            print(f"""{Fore.LIGHTBLUE_EX}
                  
            ████████╗██╗  ██╗███████╗     ██████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
            ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
               ██║   ███████║█████╗      ██║     ██████╔╝█████╗  ███████║   ██║   ██║██║   ██║██╔██╗ ██║
               ██║   ██╔══██║██╔══╝      ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
               ██║   ██║  ██║███████╗    ╚██████╗██║  ██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
               ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
""")
            time.sleep(1)
            clear_console()
            time.sleep(2)   
            

            print(f"{Fore.BLUE}In the vast emptiness before time, a spark ignited...")
            time.sleep(3)

            print(f"{Fore.CYAN}\nTwo beings, {Style.BRIGHT}Lyrian{Style.RESET_ALL} and {Style.BRIGHT}Ozla{Style.RESET_ALL}, awoke to consciousness.")
            time.sleep(wait_speed)

            print("\nThey looked upon the nothingness and, together, dreamed a universe into existence.")
            time.sleep(wait_speed)

            print(f"\nThey shaped the {Fore.YELLOW}radiant realm of Eternum{Style.RESET_ALL}, their divine home, and then breathed life into {Fore.RED}Edoria{Style.RESET_ALL}, a world of swirling molten rock, a canvas for their grand designs.")
            time.sleep(wait_speed)

            print(f"{Fore.GREEN}\nLyrian{Style.RESET_ALL}, captivated by the beauty of creation, declared himself the {Style.BRIGHT}God of Existence{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print(f"{Fore.MAGENTA}\nOzla{Style.RESET_ALL}, drawn to the mysteries of endings, became the {Style.BRIGHT}God of the End{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print("\nBut their differing perspectives sowed the seeds of discord.")
            time.sleep(wait_speed)

            print(f"\nWithin Eternum, {Fore.MAGENTA}Ozla{Style.RESET_ALL} crafted the {Fore.BLACK}{Style.BRIGHT}Shade{Style.RESET_ALL}, a realm of darkness and shadow.")
            time.sleep(wait_speed)

            print(f"{Fore.GREEN}\nLyrian{Style.RESET_ALL} sought to banish this encroaching gloom, while {Fore.MAGENTA}Ozla{Style.RESET_ALL} reveled in its growth. Their disagreement fractured their unity, birthing a corrupting force that tainted Eternum's crystalline beauty.")
            time.sleep(wait_speed)

            print(f"{Fore.RED}\nThe Divine Rift{Style.RESET_ALL} tore through their bond. {Fore.GREEN}Lyrian{Style.RESET_ALL} stood as the High Deity, championing light and life. {Fore.MAGENTA}Ozla{Style.RESET_ALL}, embracing the darkness, retreated to the {Fore.BLACK}{Style.BRIGHT}Shade{Style.RESET_ALL}, her own realm of shadows.")
            time.sleep(wait_speed)

            print(f"\nTheir feud escalated into a cosmic war, the fate of {Fore.YELLOW}Eternum{Style.RESET_ALL} hanging in the balance.")
            time.sleep(wait_speed)

            print(f"{Fore.MAGENTA}\nOzla's{Style.RESET_ALL} monstrous {Fore.RED}Corrupters{Style.RESET_ALL} clashed with {Fore.GREEN}Lyrian's{Style.RESET_ALL} radiant {Fore.CYAN}Eternals{Style.RESET_ALL} in a symphony of destruction. The {Fore.RED}First Battle of the Corruption War{Style.RESET_ALL} painted Eternum with the blood of both sides. Though the Eternals emerged victorious, the cost was immense.")
            time.sleep(wait_speed)

            print("\nThe war raged on, a celestial dance of light and shadow. But in the end, Lyrian's forces prevailed.")
            time.sleep(wait_speed)

            print(f"{Fore.MAGENTA}\nOzla{Style.RESET_ALL} and her {Fore.BLACK}{Style.BRIGHT}Shade{Style.RESET_ALL} were banished, cast out from Eternum, a testament to the perils of unchecked ambition.")
            time.sleep(wait_speed)

            print("\nIn the wake of conflict, a new dawn arose. {Fore.GREEN}Lyrian{Style.RESET_ALL}, seeking balance and order, brought forth a pantheon of {Style.BRIGHT}Lesser Deities{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print("\nThey were entrusted with the stewardship of the multiverse, guiding mortals and shaping cultures on {Fore.RED}Edoria{Style.RESET_ALL}.")
            time.sleep(wait_speed)

            print(f"\nThe echoes of the {Fore.RED}Divine Rift{Style.RESET_ALL} still reverberate through the cosmos. {Fore.RED}Edoria{Style.RESET_ALL} stands as a testament to the eternal struggle between light and darkness, creation and destruction.")
            time.sleep(wait_speed)

            print("\nThe gods may have retreated to their celestial realms, but their influence lingers, shaping the destinies of mortals and reminding them of the delicate balance upon which existence rests.")
            time.sleep(wait_speed + 3)

class Quest:
    def accept_quest_with_reward(player, reward_amount):
        player.gold += reward_amount  # Add the reward
        print(Fore.GREEN + "You have accepted the quest and received 100 gold.")
        # ... other actions (like updating quest status, etc.) ...


class NPC:
    def __init__(self, name, dialogue_data):
        self.name = name
        self.dialogue = dialogue_data  # Assign the dialogue data to the dialogue attribute

    def talk(self, player, dialogue_id=0):
        if self.dialogue[dialogue_id]:
            current_dialogue = self.dialogue[dialogue_id]
            while current_dialogue:
                clear_console()
                print(Fore.BLUE + f"{self.name}: {Fore.RESET}{current_dialogue.text}\n")
                if current_dialogue.action:
                    if current_dialogue.action == "accept_quest_with_reward":
                        Quest.accept_quest_with_reward(player, 100)

                if not current_dialogue.responses:
                    break
                for idx, response in enumerate(current_dialogue.responses):
                    print(f"{idx + 1}. {response['text']}")
                choice = input("\nEnter the number of your choice: ")
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(current_dialogue.responses):
                        next_id = current_dialogue.responses[idx]["next_id"]
                        if next_id == -1:
                            break
                        else:
                            current_dialogue = self.dialogue[next_id]
                    else:
                        print(Fore.RED + "Invalid choice.")
                        time.sleep(1)
                else:
                    print(Fore.RED + "Invalid input. Please enter a number.")
                    time.sleep(1)
            input("press Enter to continue...")
        else:
            print(f"{Fore.RED} No dialogue found for ID: {dialogue_id}{Fore.RESET}")
            time.sleep(1)

# Enemy Class
class Enemy:
    def __init__(self, enemy_data):
        self.name = enemy_data['name']
        self.level = enemy_data['level']
        self.health = enemy_data['health']
        self.ac = enemy_data['ac']
        self.attack_bonus = enemy_data['attack_bonus']
        self.damage = enemy_data['damage']
        self.gold = enemy_data['gold']
        self.locations = enemy_data['locations']


    def is_alive(self):
        return self.health > 0

# Item Class
class Item:
    def __init__(self, item_data):
        self.name = item_data['name']
        self.type = item_data['type']
        self.price = item_data.get('price', 0)
        self.effect = item_data.get('effect')
        self.value = item_data.get('value')
        self.damage = item_data.get('damage')
        self.attack_bonus = item_data.get('attack_bonus', 0)
        self.ac_bonus = item_data.get('ac_bonus', 0)

# Shop Class
class Shop:
    def __init__(self, game_data: GameData, shop_name, shop_data, npcs=[]):
        self.gamedata = game_data
        self.shop_name = shop_name
        self.shop_data = shop_data
        self.items = []
        self.populate_inventory()
        self.npcs = []
        self.player = None

    def play_shop_sfx(shop_data, file_name="shop_greeting"):
        """
        Plays a sound effect for the given shop.

        Args:
            shop_data (dict): The dictionary containing shop data (including 'merchant_id').
            file_name (str, optional): The name of the sound file (without extension). 
                Defaults to "shop_greeting".
        """
        # Play Shop Greeting
        sfx_path = os.path.join("sfx", "voiceover", shop_data.shop_data['merchant_id'], f"{file_name}.wav")
        if os.path.exists(sfx_path):
            play_sfx(sfx_path)

    def open_shop(self, player):
        self.player = player
        self.npcs.append(self.gamedata.npcs.get("Clement Bugbee"))
        self.merchant_name = self.shop_data['merchant_name']
        self.merchant_greeting = self.shop_data['merchant_greeting']
        self.merchant_goodbye = self.shop_data['merchant_goodbye']
        self.play_shop_sfx("shop_greeting") # We can add an argument later to randomize the greeting!

        # Shop Loop
        while True:
            clear_console()
            
            print_titlebar(size="large", title=f"{Fore.WHITE}Welcome to {Fore.BLUE}{self.shop_name}{Fore.YELLOW}!", color=Fore.YELLOW)
            print(f"\n{Fore.BLUE}{self.merchant_name}: {Fore.WHITE}{self.merchant_greeting}{Fore.RESET}\n")
            
            self.show_shop_inventory() #Show Shops Inventory

            print(f"{Fore.WHITE}Press {Fore.YELLOW}'{len(self.items) + 1}'{Fore.WHITE} to {Fore.RED}Exit shop{Fore.RESET}")
            print(f"{Fore.WHITE}Press {Fore.YELLOW}'{len(self.items) + 2}'{Fore.WHITE} to {Fore.CYAN}Open Inventory{Fore.RESET}")
            
            choice = input("\nWhat would you like to buy? Enter the item number: ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(self.items):
                    item = self.items[choice - 1]
                    item_price = item.price
                    if self.shop_data['inventory'][item.name]['on_sale'] == True:
                        item_price = item.price - (item.price * (self.shop_data['inventory'][item.name]['discount'] / 100))
                        item_price = int(item_price)
                    if player.gold >= item_price:
                        if self.shop_data['inventory'][item.name]['quantity'] > 0:  # Check if item is in stock
                            player.gold -= item_price
                            player.inventory.append(vars(item))
                            self.shop_data['inventory'][item.name]['quantity'] -= 1  # Decrement quantity
                            print(Fore.GREEN + f"\nYou purchased {item.name}!")
                            purchase_sfx_count = self.get_purchase_sfx_count(self.shop_data['merchant_id']) # Get the number of sfxs in a folder.
                            random_sfx_number = random.randint(1, purchase_sfx_count) # Get random sound effect.
                            play_sfx(os.path.join("sfx", "voiceover", self.shop_data['merchant_id'], f"purchase - {random_sfx_number}.wav"))
                            input("Press Enter to continue...")
                        else:
                            print(Fore.RED + f"\nSorry, {item.name} is out of stock.")
                            input("Press Enter to continue...")
                    else:
                        print(Fore.RED + "\nYou don't have enough gold.")
                        input("Press Enter to continue...")
                elif choice == len(self.items) + 1:
                    print(f"\n{Fore.BLUE}{self.merchant_name}: {Fore.WHITE}{self.merchant_goodbye}{Fore.RESET}")
                    self.play_shop_sfx("shop_goodbye")
                    time.sleep(2)
                    break
                elif choice == len(self.items) + 2: #Open Players Inventory
                    self.show_player_info(self.player)
                else:
                    print(Fore.RED + "Invalid option.")
                    time.sleep(1)
            else:
                print(Fore.RED + "Please enter a valid option.")
                time.sleep(1)

    def get_present_npcs(self):
        """
        Returns a list of NPCs whose location matches the shop's name.
        """
        present_npcs = []
        for npc_name, npc_data in Database.gamedata.npcs.items():
            if self.shop_name in npc_data.get('locations', []):  # Check if shop_name is in the locations array
                present_npcs.append(npc_name)
        return present_npcs

    def show_shop_inventory(self):
        player = self.player
        print_titlebar(size="normal", title=f"{Fore.BLUE}Shop Inventory{Fore.YELLOW}", color=Fore.YELLOW)
        print(Fore.CYAN + f"\n Your Gold \n  {Fore.YELLOW}[ {player.gold} ]\n")

        # Create PrettyTable
        table = PrettyTable()
        table.field_names = ["#", "Item", "Price", "Quantity"]
        table.align["Item"] = "l"  # Left align item name
        table.align["Price"] = "l"  # Right align price
        table.align["Quantity"] = "c"  # Right align quantity
        table.set_style(SINGLE_BORDER)

        # Populate the table
        for idx, item in enumerate(self.items):
            item_price = item.price
            sale_info = ""
            item_quantity = self.shop_data['inventory'][item.name]['quantity']
            if self.shop_data['inventory'][item.name]['on_sale']:
                item_price = item.price - (item.price * (self.shop_data['inventory'][item.name]['discount'] / 100))
                item_price = int(item_price)
                sale_info = f"{Fore.GREEN}[{self.shop_data['inventory'][item.name]['discount']}% SALE] {Fore.RESET}"
            table.add_row([idx + 1, f"{item.name}", f"{Fore.YELLOW}{item_price} gold{Fore.RESET} {sale_info}", f"{Fore.CYAN}{item_quantity}{Fore.RESET}"])

                # Print the table
        print(table)

    def show_player_info(self, player: Character):
        clear_console()
        print_titlebar(title="Player Inventory",)
        player.show_inventory_table()

    def populate_inventory(self):
        for item_name, item_data in self.shop_data['inventory'].items():
            item_data['name'] = item_name
            if item_name in self.gamedata.items:
                item_data.update(self.gamedata.items[item_name])
                item = Item(item_data)
                self.items.append(item)

    def new(gamedata, shop_name, shop_data):
        return Shop(gamedata, shop_name, shop_data)

    # Get the number of files in a folder. We can change this later to be more universal.
    def get_purchase_sfx_count(self, merchant_id):
        """
        Gets the number of "purchase" sound files for a given merchant.
        """
        sfx_dir = os.path.join("sfx", "voiceover", merchant_id)
        purchase_files = [
            f for f in os.listdir(sfx_dir) if f.startswith("purchase -") and f.endswith(".wav")
        ]
        return len(purchase_files)
    
class Database:
    gamedata = GameData()
    NPCs = {}
    shops = []
    for npc_name, npc_data in gamedata.npcs.items():
        # Create dialogue objects from JSON data
        npc_data['dialogues'] = [Dialogue(**dialogue_item) for dialogue_item in npc_data['dialogues']]
        NPCs[npc_name] = NPC(npc_name, npc_data['dialogues']) 

    def create_shops_from_data(self):
        shops = []
        for shop_name, shop_data in self.shops.items():
            shops.append(Shop(game_data=GameData, shop_name=shop_name, shop_data=shop_data))
        return shops


# ASCII Art
class Art:
    def come_again_soon(color=Fore.YELLOW):
        print(f"""{color}
              
   ____                          _               _         ____                    _ 
  / ___|___  _ __ ___   ___     / \   __ _  __ _(_)_ __   / ___|  ___   ___  _ __ | |
 | |   / _ \| '_ ` _ \ / _ \   / _ \ / _` |/ _` | | '_ \  \___ \ / _ \ / _ \| '_ \| |
 | |__| (_) | | | | | |  __/  / ___ \ (_| | (_| | | | | |  ___) | (_) | (_) | | | |_|
  \____\___/|_| |_| |_|\___| /_/   \_\__, |\__,_|_|_| |_| |____/ \___/ \___/|_| |_(_)
                                     |___/                                                                                                                                                                                                                                                                                    
""") 
    def game_over(color=Fore.RED):
        print(color + """
          ▄████  ▄▄▄       ███▄ ▄███▓▓█████     ▒█████   ██▒   █▓▓█████  ██▀███  
         ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀    ▒██▒  ██▒▓██░   █▒▓█   ▀ ▓██ ▒ ██▒
        ▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒███      ▒██░  ██▒ ▓██  █▒░▒███   ▓██ ░▄█ ▒
        ░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄    ▒██   ██░  ▒██ █░░▒▓█  ▄ ▒██▀▀█▄  
        ░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒   ░ ████▓▒░   ▒▀█░  ░▒████▒░██▓ ▒██▒
         ░▒   ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░   ░ ▒░▒░▒░    ░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░
          ░   ░   ▒   ▒▒ ░░  ░      ░ ░ ░  ░     ░ ▒ ▒░    ░ ░░   ░ ░  ░  ░▒ ░ ▒░
        ░ ░   ░   ░   ▒   ░      ░      ░      ░ ░ ░ ▒       ░░     ░     ░░   ░ 
              ░       ░  ░       ░      ░  ░       ░ ░        ░     ░  ░   ░     
                                                     ░                   
\n\n""")

# Game Class
class Game:
    player: Character
    game_data: GameData

    def parse_command(user_input, player_send):
        if game_data.DeveloperModeEnabled:
            player: Character = player_send
            command = str(user_input).replace("/", "")
            command_parts = command.split(" ")

            #Give player command
            if command_parts[0] == "give":
                player.inventory.append()
            
            if command_parts[0] == "gold":
                player.gold = int(command_parts[1])

            # Print Data command
            if command_parts[0].lower() in ['print', 'display', 'show']:

                #Show NPC table
                if command_parts[1].lower() in ['npcdata', 'npcs', 'allnpcs']:
                    print(Fore.RESET + npc_table)
                    print("\n")
                    input("Press Enter to continue...")

            else:
                input(Fore.RED + "Command not recognized. Press any key to continue.")

                # Main Game Loop

        else:
            print(f"Developer mode is {Fore.RED}disabled{Fore.RESET}.")

    def game(self, gamedata):
        game_data = gamedata
        music_thread = threading.Thread(target=play_music, args=("music.mp3",))
        music_thread.start()
        display_title_screen(game_data)
        choice, _ = select_option(['New Game', 'Load Game', 'Exit Game'], "Select an option:", clear_screen=False)
        if choice == 'Load Game':
            sfx_thread = threading.Thread(target=play_sfx, args=(os.path.join("sfx", "newgame.mp3"),))
            sfx_thread.start()
            player = load_game()

            if player:
                # Play Travel Music
                Tools.is_music_playing = False
                time.sleep(1)
                Tools.is_music_playing = True
                travel_music = threading.Thread(target=play_music, args=(os.path.join("music", "traveling.mp3"),))
                
                travel_music.start()

            if not player:
                player = create_character(game_data)
        elif choice == 'Exit Game':
            pygame.mixer.music.stop()
            print(Fore.RED + f"\n{Fore.BLUE}{game_data.title}{Fore.RED} © {game_data.year} {game_data.publisher}. All Rights Reserved.")
            sys.exit()
        else:
        #   pygame.mixer.music.stop()
            sfx_thread = threading.Thread(target=play_sfx, args=(os.path.join("sfx", "newgame.mp3"),))
            sfx_thread.start()
            player = create_character(game_data)

        # Main game flow
        while True:
            clear_console()
            location_text = Fore.YELLOW + f"You are in {Fore.BLUE}{player.location}{Fore.YELLOW}.\n"
            location = game_data.locations.get(player.location, {})
            options = ['Explore', 'Check Inventory', 'View Stats', 'Save Game', 'Quit']
            if location.get('shopPresent'):
                shops = location.get('shops', [])
                options.insert(0, f"Visit {Fore.YELLOW}Shop{Fore.RESET}")
                
            if location.get('npcs'):
                npcs = location.get('npcs', [])
                options.insert(0, f"Talk to an {Fore.BLUE}NPC{Fore.RESET}")
            choice, _ = select_option(options, f"{location_text}\nWhat would you like to do?", clear_screen=True, player_send=player)
            
            if choice.startswith(f'Visit {Fore.YELLOW}Shop{Fore.RESET}'):
                shop_list = list(game_data.shops.keys())
                
                selected_shop = select_option(shop_list, "Select a shop:", clear_screen=True)
                
                shop_name = selected_shop[0]


                Game.shop_summary(shop_name, player)

            
            
            elif choice.startswith('Talk to'):
                npc_list = location.get('npcs', [])
                choice = select_option(npc_list, "Select an NPC:")
                if choice[0] in npc_list:
                    npc_name = choice[0]
                npc = Database.NPCs.get(npc_name)
                if npc:
                    npc.talk(player)
                else:
                    print(Fore.RED + "NPC not found.")
                    input("Press Enter to continue...")
            elif choice == 'Explore':
                # Move to a new location
                locations = list(game_data.locations.keys())
                print(f"{Fore.YELLOW}Current Location:{Fore.CYAN}{player.location}{Fore.RESET}\n")
                location_choice, _ = select_option(locations + ['Back'], "Where would you like to go?", clear_screen=False)
                if location_choice != 'Back':
                    if player.location == location_choice:
                        print(f"{Fore.RED}You are already at {Fore.BLUE}{location_choice}{Fore.RESET}.")
                        time.sleep(2)
                    else:
                        player.move_to_location(location_choice, game_data)
                        # Random encounter
                        randomEncounter = random.choice([True, False])
                        if randomEncounter:
                            possible_enemies = [
                                enemy_data for enemy_data in game_data.enemies.values()
                                if player.location in enemy_data['locations']
                            ]
                            if possible_enemies:
                                # Randomly select an enemy from the valid ones
                                enemy_data = random.choice(possible_enemies)
                                enemy = Enemy(enemy_data)
                                battle(player, enemy)
                    
                else:
                    continue

            elif choice == 'Check Inventory':
                # Manage inventory
                player.show_inventory_table()
                # player.show_inventory()
            elif choice == 'View Stats':
                player.show_stats()
                input("\nPress Enter to continue...")
            elif choice == 'Save Game':
                save_game(player)
            elif choice == 'Quit':
                print(Fore.RED + "Exiting game...")
                Tools.is_music_playing = False
                sys.exit()

    def shop_summary(shop_name, player):
                    # Summary Shop (To give the player the option to enter or not)
        clear_console()
        print(print_bar("large", Fore.YELLOW))
        print(f"{Fore.LIGHTBLUE_EX}{shop_name} {Fore.RED}({game_data.shops.get(shop_name).get('type')})")
        print(f"{Fore.WHITE}\nMerchant: {Fore.RED}{game_data.shops.get(shop_name).get('merchant')}")
        print(f"{Fore.WHITE}\nDescription:\n{Fore.RED}{game_data.shops.get(shop_name).get('description')}{Fore.RESET}")
        print(print_bar("large", Fore.YELLOW))
        choice = select_option(["Yes", "No"], f"Would you like to enter {Fore.LIGHTBLUE_EX}{shop_name}{Fore.YELLOW}?{Fore.RESET}", Fore.YELLOW, False)
        # Open shop
        if choice[0] == "Yes":
            shop = Shop(game_data, shop_name, game_data.shops[shop_name])        
            # Add the merchant to the options!!
            shop.open_shop(player)
        if choice[0] == "No":
            time.sleep(1)
            clear_console()


# Battle System
def battle(player: Character, enemy: Enemy):
    # Enhanced battle system with equipment and abilities


    while enemy.is_alive() and player.health > 0:
        player.ac = player.get_ac()
        player_ac = player.ac
        if player.equipped_armor:
            player_ac += player.equipped_armor.get('ac_bonus', 0)
        clear_console()
        print_titlebar("large", f"{Fore.BLUE}{player.name}{Fore.RESET}", Fore.YELLOW)
        print(f"{Fore.BLUE}   Armor Rating: {player.ac}{Fore.RESET}")
        print(f"{Fore.RED}   HP: ({player.health}/{player.max_health}){Fore.RESET}")

        print_titlebar("large", f"{Fore.RED}{enemy.name}{Fore.YELLOW}", Fore.YELLOW)
        print(f"   HP: {enemy.health}\n")

        options = ['Attack', 'Use Ability', 'Use Item', 'Run']

        # Players Turn
        print_titlebar("large", "", Fore.YELLOW)
        action, _ = select_option(options, "Choose your action:", clear_screen=False, player_send=player)
        if action == 'Attack':
            clear_console()
            print_titlebar("normal", f"{Fore.CYAN}{player.name.upper()} TURN{Fore.YELLOW}", Fore.YELLOW)
            attack_roll = random.randint(1, 20) + player.modifiers['Strength']
            if player.equipped_weapon:
                attack_roll += player.equipped_weapon.get('attack_bonus', 0)
            time.sleep(1)
            print(f"\nYou rolled an attack of {attack_roll} vs Enemy Armor Rating {enemy.ac}")
            if attack_roll >= enemy.ac:
                damage_roll = player.equipped_weapon.get('damage', '1d4') if player.equipped_weapon else '1d4'
                damage = roll_damage(damage_roll) + player.modifiers['Strength']
                enemy.health -= damage
                time.sleep(1)
                print(Fore.GREEN + f"You hit the {enemy.name} for {damage} damage!")
            else:
                time.sleep(1)
                print(Fore.RED + "Your attack missed!")
        elif action == 'Use Ability':
            # Implement abilities based on class
            clear_console()
            use_ability(player, enemy)
        elif action == 'Use Item':
            clear_console()
            player.show_inventory_table()
        elif action == 'Flee':
            flee_chance = random.randint(1, 20) + player.modifiers['Dexterity']
            if flee_chance > 10:
                print(Fore.GREEN + f"\nYou successfully escaped with a roll of {Fore.CYAN}{flee_chance}{Fore.YELLOW}")
                input("Press Enter to continue...")
                return
            else:
                print(Fore.RED + f"\nYou failed to escape with a roll of {Fore.CYAN}{flee_chance}{Fore.RESET}")
        
        # Enemy's turn
        if enemy.is_alive():
            print()
            time.sleep(1)
            print_titlebar("normal", f"{Fore.RED}{enemy.name.upper()} TURN{Fore.YELLOW}", Fore.YELLOW)
            enemy_attack_roll = random.randint(1, 20) + enemy.attack_bonus
            time.sleep(1)
            print(f"\n{Fore.RED}{enemy.name}{Fore.RESET} attacks with a roll of {Fore.GREEN}{enemy_attack_roll}{Fore.RESET} vs Your {Fore.BLUE}Armor Rating {player_ac}{Fore.RESET}")
            if enemy_attack_roll >= player_ac:
                enemy_damage = roll_damage(enemy.damage)
                player.adjust_health(-enemy_damage)
                time.sleep(1)
                print(Fore.RED + f"{enemy.name}{Fore.RESET} hits you for {Fore.RED}{enemy_damage} damage!{Fore.RESET}")
            else:
                time.sleep(1)
                print(Fore.GREEN + f"{enemy.name}'s attack missed!")
            input("\nPress Enter to continue...")

    if player.health <= 0:
        Character.player_killed(player)
    #Defeated Enemy
    if not enemy.is_alive():
        time.sleep(2)
        print(Fore.GREEN + f"You defeated the {enemy.name}!")
        earned_exp = enemy.level * 10
        enemy_gold_loot = int(enemy.gold * random.uniform(0.33, 1.5))
        player.exp += earned_exp
        player.gold += enemy_gold_loot
        print(Fore.YELLOW + f"You gained {earned_exp} experience and found {enemy_gold_loot} gold!")
        input("Press Enter to continue...")

def use_ability(player, enemy):
    abilities = {
        'Fighter': ['Power Strike'],
        'Rogue': ['Sneak Attack'],
        'Wizard': ['Cast Spell'],
        'Cleric': ['Heal'],
        'Ranger': ['Multi-Shot'],
    }
    available_abilities = abilities.get(player.char_class, [])
    if not available_abilities:
        print(Fore.RED + "You have no abilities to use.")
        input("Press Enter to continue...")
        return
    ability, _ = select_option(available_abilities + ['Back'], "Choose an ability:", clear_screen=False)
    if ability == 'Back':
        return
    if ability == 'Power Strike':
        attack_roll = random.randint(1, 20) + player.modifiers['Strength'] + 2
        if attack_roll >= enemy.ac:
            damage = roll_damage('2d6') + player.modifiers['Strength']
            enemy.health -= damage
            print(Fore.GREEN + f"You used Power Strike and dealt {damage} damage!")
        else:
            print(Fore.RED + "Your Power Strike missed!")
    elif ability == 'Sneak Attack':
        attack_roll = random.randint(1, 20) + player.modifiers['Dexterity'] + 2
        if attack_roll >= enemy.ac:
            damage = roll_damage('3d6') + player.modifiers['Dexterity']
            enemy.health -= damage
            print(Fore.GREEN + f"You used Sneak Attack and dealt {damage} damage!")
        else:
            print(Fore.RED + "Your Sneak Attack failed!")
    elif ability == 'Cast Spell':
        damage = roll_damage('4d6') + player.modifiers['Intelligence']
        enemy.health -= damage
        print(Fore.GREEN + f"You cast a spell and dealt {damage} damage!")
    elif ability == 'Heal':
        heal_amount = roll_damage('2d8') + player.modifiers['Wisdom']
        player.adjust_health(heal_amount)
        print(Fore.GREEN + f"You healed yourself for {heal_amount} health!")
    elif ability == 'Multi-Shot':
        hits = 0
        for _ in range(2):
            attack_roll = random.randint(1, 20) + player.modifiers['Dexterity']
            if attack_roll >= enemy.ac:
                damage = roll_damage('1d8') + player.modifiers['Dexterity']
                enemy.health -= damage
                hits += 1
        print(Fore.GREEN + f"You used Multi-Shot and hit {hits} times!")

def roll_damage(damage_str: str):
    # Parses damage strings like '2d6' and returns the total damage
    num, die = damage_str.split('d')
    total = sum(random.randint(1, int(die)) for _ in range(int(num)))
    return total

def print_titlebar(size="normal", title="MENU", color=Fore.WHITE, style=Style.NORMAL):
    if size == "small":
        print(f"{color}══════════════ {title} ══════════════")
    elif size == "normal":
        print(f"{color}══════════════════════ {title} ══════════════════════")
    elif size == "large":
        print(f"{color}════════════════════════════ {title} ════════════════════════════")

def print_bar(size, color=Fore.WHITE, style=Style.NORMAL):
    if size == "small":
        return f"{color}════════════════════════════{Fore.RESET}"
    elif size == "normal":
        return f"{color}════════════════════════════════════════════{Fore.RESET}"
    elif size == "large":
        return f"{color}════════════════════════════════════════════════════════{Fore.RESET}"
def create_character(game_data):
    color = Fore.GREEN
    reset = Fore.RESET
    input_color = Fore.CYAN
    # Character Creation
    gender_options = list(["Male", "Female", "Non-binary"])
    gender_selection = select_option(gender_options, f"Choose your character's {color}gender{reset}:", clear_screen=True)
    gender = gender_selection[0]

    # Race selection
    race_names = list(game_data.races.keys())
    race, _ = select_option(race_names, f"Choose your {color}race{reset}:")

    # Background selection
    background_list = list(game_data.backgrounds.keys())
    background, _ = select_option(background_list, f"Choose your character's {color}background{reset}:")

    # Class selection
    classes_list = list(game_data.classes.keys())
    char_class, _ = select_option(classes_list, f"Choose your {color}class{reset}:")

    clear_console()
    name = input(f"  {Fore.YELLOW}Enter your character's {color}name{reset}:{input_color} ")
    # Initialize character without attributes
    player = Character(name, race, gender, background, char_class)

    # Attribute allocation
    method, _ = select_option(['Roll for stats', 'Point buy'], "Choose your attribute allocation method:")
    if method == 'Roll for stats':
        while True:
            player.attributes = player.roll_attributes()
            player.update_modifiers()
            player.max_health = player.calculate_max_health()
            player.health = player.max_health
            player.show_stats()
            print()
            choice, _ = select_option(['Accept these stats', 'Reroll'], "Do you want to keep these stats?", clear_screen=False)
            if choice == 'Accept these stats':
                break
    else:
        player.attributes = player.point_buy_attributes()
        player.update_modifiers()
        player.max_health = player.calculate_max_health()
        player.health = player.max_health
        player.show_stats()
        input("Press Enter to continue...")

    print(Fore.GREEN + "\nCharacter created successfully!")
    player.show_stats()
    input("\nPress Enter to continue...")
    clear_console
    input("Would you like some lore? (y/n)")
    if input == "y":
        Tools.tell_story("creation", "the_creation.mp3", 4, 3)
    
        # Play Travel Music
    Tools.is_music_playing = False
    time.sleep(1)
    Tools.is_music_playing = True
    travel_music = threading.Thread(target=play_music, args=(os.path.join("music", "traveling.mp3"),))
    
    travel_music.start()
    return player

def play_music(music_name, volume=0.5):
    if os.path.exists(music_name):
        pygame.mixer.init()
        pygame.mixer.music.load(music_name)
        pygame.mixer.music.play(-1)  # Loop the music
        pygame.mixer.music.set_volume(volume)  # Set volume to 50%
        while pygame.mixer.music.get_busy() and Tools.is_music_playing:
            time.sleep(1)  # Check periodically if music should stop
        pygame.mixer.music.stop()

    else:
        print(Fore.RED + f"Music file {music_name} not found.")

def play_sfx(sfx_path, delay=0, volume=1.0):
    if os.path.exists(sfx_path):
        sound = pygame.mixer.Sound(sfx_path)
        time.sleep(delay)
        sound.play()
        sound.set_volume(volume)
    else:
        print(Fore.RED + f"Sound effect file {sfx_path} not found.")

# Title Screen
def display_title_screen(game_data: GameData):
    if game_data.settings['Title SFX Enabled']:
        sfx_thread = threading.Thread(target=play_sfx, args=(os.path.join("sfx", "title.mp3"), 2))
        sfx_thread.start()

    clear_console()
    print(Fore.YELLOW + """
                 ██╗     ███████╗ ██████╗ ███████╗███╗   ██╗██████╗ ███████╗
                 ██║     ██╔════╝██╔════╝ ██╔════╝████╗  ██║██╔══██╗██╔════╝
                 ██║     █████╗  ██║  ███╗█████╗  ██╔██╗ ██║██║  ██║███████╗
                 ██║     ██╔══╝  ██║   ██║██╔══╝  ██║╚██╗██║██║  ██║╚════██║
                 ███████╗███████╗╚██████╔╝███████╗██║ ╚████║██████╔╝███████║
                 ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝""")
    print("""
                                        ████▄ ▄████  
                                        █   █ █▀   ▀ 
                                        █   █ █▀▀    
                                        ▀████ █      
                                               █     
                                                ▀ """)
    print(Fore.BLUE + """
    ███        ▄█    █▄       ▄████████         ▄████████    ▄████████    ▄████████  ▄█         ▄▄▄▄███▄▄▄▄   
▀█████████▄   ███    ███     ███    ███        ███    ███   ███    ███   ███    ███ ███       ▄██▀▀▀███▀▀▀██▄ 
   ▀███▀▀██   ███    ███     ███    █▀         ███    ███   ███    █▀    ███    ███ ███       ███   ███   ███ 
    ███   ▀  ▄███▄▄▄▄███▄▄  ▄███▄▄▄           ▄███▄▄▄▄██▀  ▄███▄▄▄       ███    ███ ███       ███   ███   ███ 
    ███     ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀          ▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ▀███████████ ███       ███   ███   ███ 
    ███       ███    ███     ███    █▄       ▀███████████   ███    █▄    ███    ███ ███       ███   ███   ███ 
    ███       ███    ███     ███    ███        ███    ███   ███    ███   ███    ███ ███▌    ▄ ███   ███   ███ 
   ▄████▀     ███    █▀      ██████████        ███    ███   ██████████   ███    █▀  █████▄▄██  ▀█   ███   █▀  
                                               ███    ███                           ▀                         \n""")
    
    print(f"{Fore.YELLOW}════════════════════════════════════════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.YELLOW}       Version {Fore.BLUE}{game_data.version}              {Fore.YELLOW}Created by {Fore.BLUE}{game_data.developer} {game_data.year}")
    print(f"{Fore.YELLOW}════════════════════════════════════════════════════════════════════════════════════════════════════════════\n")

if __name__ == "__main__":
    game_data = GameData()
    game_object = Game()
    try:
        if game_data.DeveloperModeEnabled:
            clear_console()
            print(Fore.CYAN + f"Developer mode: {Fore.GREEN}ENABLED{Fore.RESET}")
            print(Fore.CYAN + f"Loading data...{Fore.RESET}\n\n")
            time.sleep(2)

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
            npc_table.title = f"{Fore.YELLOW}NPCs{Fore.RESET}"
            npc_table.border = True
            npc_table.add_column("Name", npc_names)
            npc_table.add_column("Type", npc_types)
            npc_table.add_column("Role", npc_roles)
            npc_table.add_column("Location", npc_locations)

            npc_table.set_style(DOUBLE_BORDER)
            npc_table.align = "l"
            npc_table.sortby = "Type"


            print(npc_table)
            input(f"{Fore.YELLOW}\npress any key to continue...")
                
            
        game_object.game(game_data)
    except KeyboardInterrupt:
        print(Fore.RED + "\nGame exited.")
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {e}")
