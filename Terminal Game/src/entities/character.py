"""
Character class representing the player character in the game.
"""
import random
import time
import threading
import os
import sys
from colorama import Fore
from ..ui.display import clear_console, print_titlebar
from ..ui.menus import select_option
from ..utils.tools import Tools

try:
    from prettytable import FRAME, DOUBLE_BORDER
except ImportError:
    # Import from our fallback implementation in tools
    from ..utils.tools import FRAME, DOUBLE_BORDER


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
        self.state = ""

    def roll_attributes(self):
        """Roll attributes using 4d6 drop lowest method."""
        attributes = {}
        for attr in ['Strength', 'Dexterity', 'Fortitude', 'Intelligence', 'Wisdom', 'Charisma']:
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            attributes[attr] = sum(rolls)
        return attributes
    
    def get_ac(self):
        """Calculate and return armor class."""
        self.ac = 10 + self.modifiers['Dexterity']
        if self.equipped_armor:
            self.ac += self.equipped_armor.get('ac_bonus', 0)
        return self.ac

    def point_buy_attributes(self):
        """Point buy system for attribute allocation."""
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
        """Update ability modifiers based on attributes."""
        self.modifiers = {attr: (score - 10) // 2 for attr, score in self.attributes.items()}

    def initialize_skills(self):
        """Initialize skill list with their governing attributes."""
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
        """Set class-specific attributes and proficiencies."""
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

    def set_background_attributes(self):
        """Set background-specific attributes, proficiencies, and starting equipment."""
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
        """Get starting equipment based on background and class."""
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
        """Calculate maximum health based on class and constitution."""
        return self.class_hp + self.modifiers['Fortitude']

    def level_up(self):
        """Handle character level up."""
        self.level += 1
        hp_increase = random.randint(1, self.class_hp) + self.modifiers['Fortitude']
        self.max_health += max(1, hp_increase)
        self.health = self.max_health
        print(Fore.YELLOW + f"\nYou have leveled up to Level {self.level}!")
        print(Fore.GREEN + f"Your maximum health increased by {max(1, hp_increase)}!")
        self.choose_skill_improvement()
        input("Press Enter to continue...")

    def choose_skill_improvement(self):
        """Allow player to choose a skill improvement on level up."""
        print(Fore.CYAN + "\nChoose a skill to improve:")
        skill_choices = list(set(self.skills.keys()) - set(self.proficiencies))
        if not skill_choices:
            print("You have already mastered all skills!")
            return
        skill_choice, _ = select_option(skill_choices, clear_screen=False)
        self.proficiencies.append(skill_choice)
        print(Fore.GREEN + f"You have gained proficiency in {skill_choice}!")

    def adjust_health(self, amount):
        """Adjust character health within bounds."""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health < 0:
            self.health = 0

    def show_stats(self, clear=True):
        """Display character stats and information."""
        if clear:
            clear_console()
        print_titlebar("CHARACTER SHEET", color=Fore.BLUE)
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
        """Equip a weapon or armor item."""
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
        """Move character to a new location."""
        if location_name in game_data.locations:
            self.location = location_name
            location = game_data.locations[location_name]
            clear_console()

            print(Fore.YELLOW + f"\nYou travel to {Fore.CYAN}{location['name']}{Fore.RESET}.")
            print(location.get('description', ''))
            input("Press Enter to continue...")
        else:
            print(Fore.RED + "That location does not exist.")

    def show_inventory_table(self):
        """Display inventory in table format."""
        clear_console()
        print_titlebar("INVENTORY", color=Fore.YELLOW)

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
        if hasattr(table, 'min_width'):
            table.min_width = 1
        console_width = Tools.get(Tools.Values.CONSOLE_WIDTH)
        if hasattr(table, 'max_table_width') and console_width:
            table.max_table_width = console_width - 3
        if hasattr(table, 'min_table_width'):
            table.min_table_width = 50
        if hasattr(table, 'set_style'):
            if DOUBLE_BORDER:
                table.set_style(DOUBLE_BORDER)
        print(table)

        # Get user input
        print(f"    {len(self.inventory) + 1}. {Fore.RED}Back{Fore.RESET}")
        choice = input("\nSelect an item to use or equip, or press the number for 'Back': ")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(self.inventory):
                selected_item = self.inventory[choice - 1]
                self.use_item(selected_item)
            else:
                return  # Go back
        else:
            print(Fore.RED + "Invalid input.")
            time.sleep(1)

    def use_item(self, item):
        """Use or equip an item from inventory."""
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

    @staticmethod
    def player_killed(player):
        """Handle player death."""
        if "Second Life" in player.abilities:
            print("")
        else:
            clear_console()
            Tools.is_music_playing = False
            
            # Import here to avoid circular imports
            from ..ui.art import Art
            from ..audio.audio import Audio
            
            Art.game_over(Fore.RED)
            time.sleep(2)
            Tools.is_music_playing = True
            music_thread = threading.Thread(target=Audio.play_music, args=(os.path.join("music", "game_over.mp3"),))
            music_thread.start()
            time.sleep(8)
            clear_console()
            choice = input("Would you like to continue? (Y/N): ")
            if choice.lower() == "y":
                from ..core.game import Game
                from ..data.database import GameData
                game_instance = Game()
                game_instance.game(GameData())
                Tools.is_music_playing = False
            else:
                clear_console()
                print("Thanks for playing!!\n")
                Tools.is_music_playing = True
                sys.exit()
