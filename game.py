import random
import time
import os
import json
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Utility Functions
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_option(options, title="Select an option:", clear_screen=True):
    while True:
        if clear_screen:
            clear_console()
        print(Fore.YELLOW + title)
        for idx, option in enumerate(options):
            print(f"{idx + 1}. {option}")
        choice = input("\nEnter the number of your choice: ")
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(options):
                if clear_screen:
                    clear_console()
                return options[index], index
            else:
                print(Fore.RED + "Invalid choice. Please select a valid option.\n")
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
        self.items = self.load_items()
        self.npcs = self.load_npcs()
        self.enemies = self.load_enemies()
        self.quests = self.load_quests()
        self.locations = self.load_locations()

    def load_items(self):
        # Items data
        items = {
            'Healing Potion': {'name': 'Healing Potion', 'type': 'consumable', 'price': 50, 'effect': 'heal', 'value': 15},
            'Short Sword': {'name': 'Short Sword', 'type': 'weapon', 'price': 100, 'damage': '1d6', 'attack_bonus': 1},
            'Leather Armor': {'name': 'Leather Armor', 'type': 'armor', 'price': 75, 'ac_bonus': 1},
            'Spellbook': {'name': 'Spellbook', 'type': 'misc', 'price': 200},
            'Fireball Scroll': {'name': 'Fireball Scroll', 'type': 'spell', 'price': 150, 'damage': '2d6'},
            'Steel Shield': {'name': 'Steel Shield', 'type': 'armor', 'price': 120, 'ac_bonus': 2},
        }
        return items

    def load_npcs(self):
        # NPCs data
        npcs = {
            # Previous NPCs remain the same
            # Additional NPCs can be added here
        }
        return npcs

    def load_enemies(self):
        # Enemies data
        enemies = {
            # Previous enemies remain the same
            # Additional enemies can be added here
        }
        return enemies

    def load_quests(self):
        # Quests data (not fully implemented in this version)
        quests = {}
        return quests

    def load_locations(self):
        # Locations data
        locations = {
            'Village': {
                'name': 'Village',
                'description': 'A small, peaceful village surrounded by forests.',
                'npcs': ['Elder'],
                'shop': True
            },
            'Forest': {
                'name': 'Forest',
                'description': 'A dense forest filled with towering trees and hidden dangers.',
                'enemies': ['Goblin', 'Wolf'],
                'npcs': []
            },
            'Capital City': {
                'name': 'Capital City',
                'description': 'A bustling city with towering walls and a magnificent castle.',
                'npcs': ['King'],
                'shop': True
            },
            'Dragon\'s Lair': {
                'name': 'Dragon\'s Lair',
                'description': 'A dark cave nestled in the mountains, home to the ancient dragon.',
                'enemies': ['Ancient Dragon'],
                'npcs': []
            }
        }
        return locations

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
            attr_choice, _ = select_option(list(attributes.keys()), "Select an attribute to increase:")
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

    def show_stats(self):
        print(Fore.CYAN + f"\nName: {self.name}")
        print(Fore.CYAN + f"Gender: {self.gender}")
        print(Fore.CYAN + f"Race: {self.race}")
        print(Fore.CYAN + f"Class: {self.char_class}")
        print(Fore.CYAN + f"Background: {self.background}")
        print(Fore.CYAN + f"Level: {self.level}")
        print(Fore.RED + f"Health: {self.health}/{self.max_health}")
        print(Fore.YELLOW + "Attributes:")
        for attr, score in self.attributes.items():
            mod = self.modifiers[attr]
            print(f"  {attr}: {score} ({mod:+})")
        print(Fore.MAGENTA + f"Experience: {self.exp}")
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
            print(Fore.YELLOW + f"\nYou travel to {location['name']}.")
            print(location['description'])
            input("Press Enter to continue...")
        else:
            print(Fore.RED + "That location does not exist.")

# NPC Class
class NPC:
    # NPC class remains similar
    pass  # For brevity, we'll assume it remains the same as previous versions

# Enemy Class
class Enemy:
    # Enemy class remains similar
    pass  # For brevity, we'll assume it remains the same as previous versions

# Item Class
class Item:
    # Item class remains similar
    pass  # For brevity, we'll assume it remains the same as previous versions

# Shop Class
class Shop:
    # Shop class remains similar
    pass  # For brevity, we'll assume it remains the same as previous versions

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
        action, _ = select_option(options, "Choose your action:", clear_screen=False)
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
            # Same as before
            pass
        elif action == 'Run':
            # Same as before
            pass
        # Enemy's turn
        # Same as before
        pass  # For brevity, details are omitted

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
        # Implement Power Strike ability
        pass  # Details omitted for brevity
    elif ability == 'Sneak Attack':
        # Implement Sneak Attack ability
        pass  # Details omitted for brevity
    elif ability == 'Cast Spell':
        # Implement spell casting
        pass  # Details omitted for brevity
    elif ability == 'Heal':
        # Implement Heal ability
        pass  # Details omitted for brevity
    elif ability == 'Multi-Shot':
        # Implement Multi-Shot ability
        pass  # Details omitted for brevity

def roll_damage(damage_str):
    # Parses damage strings like '2d6' and returns the total damage
    num, die = damage_str.split('d')
    total = sum(random.randint(1, int(die)) for _ in range(int(num)))
    return total

# Main Game Loop
def game():
    game_data = GameData()
    display_title_screen()
    # Option to load a saved game
    choice, _ = select_option(['New Game', 'Load Game'], "Select an option:")
    if choice == 'Load Game':
        player = load_game()
        if not player:
            player = create_character()
    else:
        player = create_character()
    # Main game flow
    while True:
        clear_console()
        print(Fore.YELLOW + f"You are in {player.location}.")
        location = game_data.locations.get(player.location, {})
        options = ['Explore', 'Check Inventory', 'View Stats', 'Save Game', 'Quit']
        if location.get('shop'):
            options.insert(0, 'Visit Shop')
        choice, _ = select_option(options, "What would you like to do?", clear_screen=False)
        if choice == 'Visit Shop':
            # Open shop
            pass  # Details omitted for brevity
        elif choice == 'Explore':
            # Move to a new location
            locations = list(game_data.locations.keys())
            location_choice, _ = select_option(locations + ['Back'], "Where would you like to go?", clear_screen=False)
            if location_choice != 'Back':
                player.move_to_location(location_choice, game_data)
        elif choice == 'Check Inventory':
            # Manage inventory
            pass  # Details omitted for brevity
        elif choice == 'View Stats':
            player.show_stats()
            input("\nPress Enter to continue...")
        elif choice == 'Save Game':
            save_game(player)
        elif choice == 'Quit':
            print(Fore.RED + "Thank you for playing!")
            break

def create_character():
    # Character Creation
    name = input("Enter your character's name: ")
    gender = input("Enter your character's gender: ")

    # Race selection
    races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Orc']
    race, _ = select_option(races, "Choose your race:")

    # Background selection
    backgrounds = ['Noble', 'Soldier', 'Scholar', 'Criminal', 'Hermit']
    background, _ = select_option(backgrounds, "Choose your background:")

    # Class selection
    classes = ['Fighter', 'Rogue', 'Wizard', 'Cleric', 'Ranger']
    char_class, _ = select_option(classes, "Choose your class:")

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
            choice, _ = select_option(['Accept these stats', 'Reroll'], "Do you want to keep these stats?", clear_screen=False)
            if choice == 'Accept these stats':
                break
    else:
        player.attributes = player.point_buy_attributes()
        player.update_modifiers()
        player.max_health = player.calculate_max_health()
        player.health = player.max_health
        player.show_stats()
        input("\nPress Enter to continue...")

    print(Fore.GREEN + "\nCharacter created successfully!")
    player.show_stats()
    input("\nPress Enter to continue...")
    return player

# Title Screen
def display_title_screen():
    clear_console()
    print(Fore.YELLOW + "========================================")
    print(Fore.CYAN + "          Legends of the Realm")
    print(Fore.CYAN + "             Version 0.11")
    print(Fore.YELLOW + "========================================\n")
    input("Press Enter to start your adventure...")

if __name__ == "__main__":
    try:
        game()
    except KeyboardInterrupt:
        print(Fore.RED + "\nGame exited.")
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {e}")
