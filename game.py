from enum import Enum
import random
import time
import os
import json
from colorama import init, Fore, Style
import pygame
import threading
import sys

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
                parse_command(choice, player_send=player)
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
        print(Fore.GREEN + "Game loaded successfully!")
        input("Press Enter to continue...")
        return player
    else:
        print(Fore.RED + "No saved game found.")
        input("Press Enter to continue...")
        return None

# Game Data
class GameData:
    def __init__(self):
        self.items = self.load_data("items.json")
        self.npcs = self.load_data("npcs.json")
        self.enemies = self.load_data("enemies.json")
        self.quests = self.load_data("quests.json")
        self.locations = self.load_data("locations.json")
        self.races = self.load_data("races.json")
        self.backgrounds = self.load_data("backgrounds.json")
        self.classes = self.load_data("classes.json")
        self.game_info = self.load_data("gameinfo.json")
        self.settings = self.load_data("settings.json")

        
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

    def roll_attributes(self):
        attributes = {}
        for attr in ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']:
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
            attributes[attr] = sum(rolls)
        return attributes

    def point_buy_attributes(self):
        attributes = {'Strength': 8, 'Dexterity': 8, 'Constitution': 8,
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
        return self.class_hp + self.modifiers['Constitution']

    def level_up(self):
        self.level += 1
        hp_increase = random.randint(1, self.class_hp) + self.modifiers['Constitution']
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
            print(Fore.GREEN + f"You have equipped {item['name']}.")
        else:
            print(Fore.RED + f"You cannot equip {item['name']}.")

    def move_to_location(self, location_name, game_data):
        if location_name in game_data.locations:
            self.location = location_name
            location = game_data.locations[location_name]
            clear_console()
            print(Fore.YELLOW + f"\nYou travel to {location['name']}.")
            print(location.get('description', ''))
            input("Press Enter to continue...")
        else:
            print(Fore.RED + "That location does not exist.")

    def show_inventory(self):
        clear_console()
        print_titlebar("normal", "INVENTORY", Fore.YELLOW)
        if not self.inventory:
            print(Fore.RED + "Your inventory is empty.")
            input("\nPress Enter to continue...")
            return
        for idx, item in enumerate(self.inventory):
            item_type = item.get('type', 'Unknown')
            print(f"{idx + 1}. {Fore.LIGHTGREEN_EX}{item['name']} {Fore.RESET}-- {Fore.BLUE}[{str(item_type).upper()}]{Fore.RESET}")
        print(f"{len(self.inventory) + 1}. {Fore.RED}Back{Fore.RESET}")
        choice = input("\nSelect an item to use or equip, or press the number for 'Back': ")
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(self.inventory):
                selected_item = self.inventory[choice - 1]
                self.use_item(selected_item)
            else:
                return
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

class Dialogue:
    def __init__(self, text, responses=None, action=None):
        self.text = text  # The dialogue text displayed by the NPC
        self.responses = responses if responses is not None else []
        self.action = action  # Optional function to execute when this dialogue is reached


# NPC Class
class NPC:
    def __init__(self, npc_data):
        self.name = npc_data.get('name', 'Unknown')
        self.role = npc_data.get('role', 'Unknown')
        self.location = npc_data.get('location', 'Unknown')
        self.relationship_score = npc_data.get('default_relationship', 0)
        self.relationship_label = "Neutral"
        self.dialogue_root = npc_data.get('dialogues')

    def talk(self, player):
        current_dialogue = self.dialogue_root
        while current_dialogue:
            clear_console()
            print(Fore.BLUE + f"{self.name}: {current_dialogue.text}\n")
            if current_dialogue.action:
                current_dialogue.action(player)
            if not current_dialogue.responses:
                break
            for idx, response in enumerate(current_dialogue.responses):
                print(f"{idx + 1}. {response.text}")
            choice = input("\nEnter the number of your choice: ")
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(current_dialogue.responses):
                    current_dialogue = current_dialogue.responses[idx]
                else:
                    print(Fore.RED + "Invalid choice.")
                    time.sleep(1)
            else:
                print(Fore.RED + "Invalid input. Please enter a number.")
                time.sleep(1)

    # A simple relationship check
    def check_relationship(rel_score):
        if rel_score == 0:
            return "Neutral"
        elif rel_score > 0:
            return "Positive"
        else:
            return "Negative"


class Database:
    gamedata = GameData()
    NPCs = {}
    for npc_name, npc_data in gamedata.npcs.items():
        NPCs[npc_name] = NPC(npc_data)



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
    def __init__(self, game_data, player):
        self.items = [Item(item_data) for item_data in game_data.items.values()]
        self.gamedata = game_data

    def open_shop(self, player, game_data):
        while True:
            clear_console()
            print(Fore.YELLOW + "\nWelcome to the shop!")
            print(Fore.YELLOW + f"You have {player.gold} gold.")
            print("\nAvailable items:")
            for idx, item in enumerate(self.items):
                print(f"{idx + 1}. {item.name} - {item.price} gold")
            print(f"{len(self.items) + 1}. Exit shop")
            choice = input("\nWhat would you like to buy? Enter the item number: ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(self.items):
                    item = self.items[choice - 1]
                    if player.gold >= item.price:
                        player.gold -= item.price
                        player.inventory.append(vars(item))
                        print(Fore.GREEN + f"\nYou purchased {item.name}!")
                        input("Press Enter to continue...")
                    else:
                        print(Fore.RED + "\nYou don't have enough gold.")
                        input("Press Enter to continue...")
                elif choice == len(self.items) + 1:
                    print("Thank you for visiting!")
                    time.sleep(1)
                    break
                else:
                    print(Fore.RED + "Invalid option.")
                    time.sleep(1)
            else:
                print(Fore.RED + "Please enter a valid option.")
                time.sleep(1)

# Battle System
def battle(player, enemy):
    # Enhanced battle system with equipment and abilities
    while enemy.is_alive() and player.health > 0:
        clear_console()
        print(Fore.RED + f"\nYou are battling a {enemy.name}!")
        print(f"\nYour Health: {player.health}/{player.max_health}")
        print(f"{enemy.name} Health: {enemy.health}")
        player_ac = 10 + player.modifiers['Dexterity']
        if player.equipped_armor:
            player_ac += player.equipped_armor.get('ac_bonus', 0)
        print(f"Your AC: {player_ac}")
        options = ['Attack', 'Use Ability', 'Use Item', 'Run']
        action, _ = select_option(options, "Choose your action:", clear_screen=False, player_send=player)
        if action == 'Attack':
            attack_roll = random.randint(1, 20) + player.modifiers['Strength']
            if player.equipped_weapon:
                attack_roll += player.equipped_weapon.get('attack_bonus', 0)
            print(f"\nYou rolled an attack of {attack_roll} vs Enemy AC {enemy.ac}")
            if attack_roll >= enemy.ac:
                damage_roll = player.equipped_weapon.get('damage', '1d4') if player.equipped_weapon else '1d4'
                damage = roll_damage(damage_roll) + player.modifiers['Strength']
                enemy.health -= damage
                print(Fore.GREEN + f"You hit the {enemy.name} for {damage} damage!")
            else:
                print(Fore.RED + "Your attack missed!")
        elif action == 'Use Ability':
            # Implement abilities based on class
            use_ability(player, enemy)
        elif action == 'Use Item':
            player.show_inventory()
        elif action == 'Run':
            run_chance = random.randint(1, 20) + player.modifiers['Dexterity']
            if run_chance > 10:
                print(Fore.YELLOW + "You successfully escaped!")
                input("Press Enter to continue...")
                return
            else:
                print(Fore.RED + "You failed to escape!")
        # Enemy's turn
        if enemy.is_alive():
            enemy_attack_roll = random.randint(1, 20) + enemy.attack_bonus
            print(f"\n{Fore.RED}{enemy.name}{Fore.RESET} attacks with a roll of {Fore.GREEN}{enemy_attack_roll}{Fore.RESET} vs Your {Fore.BLUE}AC {player_ac}{Fore.RESET}")
            if enemy_attack_roll >= player_ac:
                enemy_damage = roll_damage(enemy.damage)
                player.adjust_health(-enemy_damage)
                print(Fore.RED + f"{enemy.name} hits you for {enemy_damage} damage!")
            else:
                print(Fore.GREEN + f"{enemy.name}'s attack missed!")
            input("\nPress Enter to continue...")

    if player.health <= 0:
        print(Fore.RED + "You have been defeated!")
        input("Press Enter to continue...")
        # Handle player defeat (e.g., game over, respawn)
    elif not enemy.is_alive():
        print(Fore.GREEN + f"You defeated the {enemy.name}!")
        player.exp += enemy.level * 10
        player.gold += enemy.gold
        print(Fore.YELLOW + f"You gained {enemy.level * 10} experience and found {enemy.gold} gold!")
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

def roll_damage(damage_str):
    # Parses damage strings like '2d6' and returns the total damage
    num, die = damage_str.split('d')
    total = sum(random.randint(1, int(die)) for _ in range(int(num)))
    return total

class Game:
    player: Character

    def parse_command(user_input, player_send):
        player: Character = player_send
        command = str(user_input).replace("/", "")
        command_parts = command.split(" ")
        if command_parts[0] == "give":
            player.inventory.append()
        else:
            input(Fore.RED + "Command not recognized. Press any key to continue.")

            # Main Game Loop
    def game(gamedata):
        game_data = gamedata
        music_thread = threading.Thread(target=play_music, args=("music.mp3",))
        music_thread.start()
        display_title_screen(game_data)
        choice, _ = select_option(['New Game', 'Load Game', 'Exit Game'], "Select an option:", clear_screen=False)
        if choice == 'Load Game':
            pygame.mixer.music.stop()
            player = load_game()
            if not player:
                player = create_character(game_data)
        elif choice == 'Exit Game':
            pygame.mixer.music.stop()
            print(Fore.RED + f"\n{Fore.BLUE}{game_data.title}{Fore.RED} © {game_data.year} {game_data.publisher}. All Rights Reserved.")
            sys.exit()
        else:
            pygame.mixer.music.stop()
            sfx_thread = threading.Thread(target=play_sfx, args=(os.path.join("sfx", "newgame.mp3"),))
            sfx_thread.start()
            player = create_character(game_data)

        # Main game flow
        while True:
            clear_console()
            location_text = Fore.YELLOW + f"You are in {player.location}."
            location = game_data.locations.get(player.location, {})
            options = ['Explore', 'Check Inventory', 'View Stats', 'Save Game', 'Quit']
            if location.get('shop'):
                options.insert(0, 'Visit Shop')
            if location.get('npc'):
                options.insert(0, f"Talk to {location['npc']}")
            choice, _ = select_option(options, f"{location_text}\nWhat would you like to do?", clear_screen=True, player_send=player)
            if choice == 'Visit Shop':
                # Open shop
                shop = Shop(game_data)
                shop.open_shop(player, game_data)
                sfx_thread = threading.Thread(target=play_sfx, args=(os.path.join("sfx", "shop.mp3"),))
                sfx_thread.start()
            elif choice.startswith('Talk to'):
                npc_name = choice.replace('Talk to ', '')
                npc = Database.NPCs.get(npc_name)
                if npc:
                    npc.talk(player)
                else:
                    print(Fore.RED + "NPC not found.")
                    input("Press Enter to continue...")
            elif choice == 'Explore':
                # Move to a new location
                locations = list(game_data.locations.keys())
                location_choice, _ = select_option(locations + ['Back'], "Where would you like to go?", clear_screen=False)
                if location_choice != 'Back':
                    player.move_to_location(location_choice, game_data)
                    # Random encounter
                    if random.choice([True, False]):
                        enemy_data = random.choice(list(game_data.enemies.values()))
                        enemy = Enemy(enemy_data)
                        battle(player, enemy)
            elif choice == 'Check Inventory':
                # Manage inventory
                player.show_inventory()
            elif choice == 'View Stats':
                player.show_stats()
                input("\nPress Enter to continue...")
            elif choice == 'Save Game':
                save_game(player)
            elif choice == 'Quit':
                print(Fore.RED + "Exiting game...")
                sys.exit()
    


         
                

def print_titlebar(size="normal", title="MENU", color=Fore.WHITE, style=Style.NORMAL):
    if size == "small":
        print(f"{color}══════════════ {title} ══════════════")
    elif size == "normal":
        print(f"{color}══════════════════════ {title} ══════════════════════")
    elif size == "large":
        print(f"{color}════════════════════════════ {title} ════════════════════════════")

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
    return player

def play_music(music_name):
    if os.path.exists(music_name):
        pygame.mixer.init()
        pygame.mixer.music.load(music_name)
        pygame.mixer.music.play(-1)  # Loop the music
    else:
        print(Fore.RED + f"Music file {music_name} not found.")

def play_sfx(sfx_path, delay=0):
    if os.path.exists(sfx_path):
        sound = pygame.mixer.Sound(sfx_path)
        time.sleep(delay)
        sound.play()
    else:
        print(Fore.RED + f"Sound effect file {sfx_path} not found.")

# Title Screen
def display_title_screen(game_data):
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
            print(Fore.CYAN + f"Developer mode: {Fore.GREEN}ENABLED{Fore.RESET}.")
            time.sleep(2)
            print(Fore.YELLOW + "\n========= NPCS LOADED =========")
            for npc_data in game_data.npcs:
                npc = game_data.npcs[npc_data]
                name = npc['name']
                location = npc['location']
                role = npc["role"]

# v1            print(f"    {Fore.BLUE}{name}{Fore.RESET} the {Fore.CYAN}{role}{Fore.RESET} from {Fore.GREEN}{location}{Fore.RESET}")
# v2            print(f"    {Fore.CYAN}{role}{Fore.RESET} {Fore.BLUE}{name}{Fore.RESET} from {Fore.GREEN}{location}{Fore.RESET}")
                
                print(f"    {Fore.BLUE}{name}{Fore.RESET}   {Fore.LIGHTRED_EX}({role}){Fore.RESET}      from {Fore.GREEN}'{location}'{Fore.RESET}")
                time.sleep(0.5)
            time.sleep(5)
            input(f"{Fore.YELLOW}press any key to continue...")
                
            
        game_object.game(game_data)
    except KeyboardInterrupt:
        print(Fore.RED + "\nGame exited.")
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {e}")
