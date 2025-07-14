"""
Core game loop and main game logic.
"""
import os
import sys
import time
import random
import threading
import pygame
from colorama import Fore, Style
from ..ui.display import clear_console, print_titlebar
from ..ui.menus import select_option
from ..ui.art import Art
from ..entities.character import Character
from ..entities.enemy import Enemy
from ..systems.shop import Shop
from ..data.loader import Database
from ..audio.audio import Audio
from ..utils.helpers import save_game, load_game
from ..utils.tools import Tools

try:
    from prettytable import PrettyTable, DOUBLE_BORDER
except ImportError:
    from ..utils.tools import PrettyTable, DOUBLE_BORDER


class Game:
    def __init__(self):
        self.player = None
        self.game_data = None

    @staticmethod
    def parse_command(user_input, player_send):
        """Parse and execute developer commands."""
        from ..data.database import GameData
        
        game_data = GameData()  # Create a local instance for commands
        
        if game_data.DeveloperModeEnabled:
            player = player_send
            command = str(user_input).replace("/", "")
            command_parts = command.split(" ")

            # Give player command
            if command_parts[0] == "give":
                if len(command_parts) > 1:
                    item_name = command_parts[1]
                    print(f"Give {item_name} functionality not yet implemented")
                else:
                    print("Give command needs an item name")
            
            if command_parts[0] == "gold":
                player.gold = int(command_parts[1])

            if command_parts[0] in ['battle', 'fight']:
                enemy_data = game_data.enemies.get(command_parts[1])
                if enemy_data:
                    enemy = Enemy(enemy_data)
                    battle(player, enemy)
                else:
                    print(f"{Fore.RED}Enemy not found.")
                    time.sleep(1)
                    
            # Print Data command
            if command_parts[0].lower() in ['print', 'display', 'show']:
                # Show NPC table
                if command_parts[1].lower() in ['npcdata', 'npcs', 'allnpcs']:
                    npc_names = []
                    npc_roles = []
                    npc_types = []
                    npc_locations = []

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
                    
                    print(Fore.RESET + str(npc_table))
                    print("\n")
                    input("Press Enter to continue...")
            
            # Flee battle or shop
            if command_parts[0].lower() in ['flee', 'run', 'escape', 'leave']:
                if player.state == "battle":
                    player.state = "flee"
            else:
                input(Fore.RED + "Command not recognized. Press any key to continue.")
        else:
            print(f"Developer mode is {Fore.RED}disabled{Fore.RESET}.")

    def game(self, gamedata):
        """Main game loop."""
        self.game_data = gamedata
        
        # Start background music
        music_thread = threading.Thread(target=Audio.play_music, args=("music.mp3",))
        music_thread.start()
        
        display_title_screen(gamedata)
        choice, _ = select_option(['New Game', 'Load Game', 'Exit Game'], "Select an option:", clear_screen=False)
        
        if choice == 'Load Game':
            sfx_thread = threading.Thread(target=Audio.play_sfx, args=(os.path.join("sfx", "newgame.mp3"),))
            sfx_thread.start()
            player = load_game()

            if player:
                # Play Travel Music
                Tools.is_music_playing = False
                time.sleep(1)
                Tools.is_music_playing = True
                travel_music = threading.Thread(target=Audio.play_music, args=(os.path.join("music", "traveling.mp3"),))
                travel_music.start()

            if not player:
                player = create_character(gamedata)
                
        elif choice == 'Exit Game':
            pygame.mixer.music.stop()
            print(Fore.RED + f"\n{Fore.BLUE}{gamedata.title}{Fore.RED} © {gamedata.year} {gamedata.publisher}. All Rights Reserved.")
            sys.exit()
        else:
            sfx_thread = threading.Thread(target=Audio.play_sfx, args=(os.path.join("sfx", "newgame.mp3"),))
            sfx_thread.start()
            player = create_character(gamedata)

        self.player = player

        # Main game flow
        while True:
            clear_console()
            location = gamedata.locations.get(player.location, {})
            options = ['Explore', 'Check Inventory', 'View Stats', 'Save Game', 'Quit']
            
            if location.get('shopPresent'):
                options.insert(0, f"Visit {Fore.YELLOW}Shop{Fore.RESET}")
                
            if location.get('npcs'):
                options.insert(0, f"Talk to an {Fore.BLUE}NPC{Fore.RESET}")
            
            print_titlebar(f"{Fore.BLUE}{player.location}{Fore.YELLOW}", color=Fore.YELLOW)
            
            choice, _ = select_option(options, f"What would you like to do?", clear_screen=False, player_send=player)
            
            clear_console()

            if choice.startswith(f'Visit {Fore.YELLOW}Shop{Fore.RESET}'):
                shop_list = list(gamedata.shops.keys())
                selected_shop = select_option(shop_list, "Select a shop:", clear_screen=True)
                shop_name = selected_shop[0]
                Game.shop_summary(shop_name, player, gamedata)
            
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
                locations = list(gamedata.locations.keys())
                print(f"{Fore.YELLOW}Current Location:{Fore.CYAN}{player.location}{Fore.RESET}\n")
                location_choice, _ = select_option(locations + ['Back'], "Where would you like to go?", clear_screen=False)
                if location_choice != 'Back':
                    if player.location == location_choice:
                        print(f"{Fore.RED}You are already at {Fore.BLUE}{location_choice}{Fore.RESET}.")
                        time.sleep(2)
                    else:
                        player.move_to_location(location_choice, gamedata)
                        # Random encounter
                        randomEncounter = random.choice([True, False])
                        if randomEncounter:
                            possible_enemies = [
                                enemy_data for enemy_data in gamedata.enemies.values()
                                if player.location in enemy_data['locations']
                            ]
                            if possible_enemies:
                                enemy_data = random.choice(possible_enemies)
                                enemy = Enemy(enemy_data)
                                battle(player, enemy)
                else:
                    continue

            elif choice == 'Check Inventory':
                player.show_inventory_table()
            elif choice == 'View Stats':
                player.show_stats()
                input("\nPress Enter to continue...")
            elif choice == 'Save Game':
                save_game(player)
            elif choice == 'Quit':
                print(Fore.RED + "Exiting game...")
                Tools.is_music_playing = False
                time.sleep(2)
                sys.exit()

    @staticmethod
    def shop_summary(shop_name, player, game_data):
        """Display shop summary and handle entry."""
        clear_console()
        
        shop_data = game_data.shops.get(shop_name)
        if not shop_data:
            print(f"{Fore.RED}Error: Shop '{shop_name}' not found in shop data!{Fore.RESET}")
            input("Press Enter to continue...")
            return
            
        print(print_bar("large", Fore.YELLOW))
        print(f"{Fore.LIGHTBLUE_EX}{shop_name} {Fore.RED}({shop_data.get('type', 'Unknown')})")
        print(f"{Fore.WHITE}\nMerchant: {Fore.RED}{shop_data.get('merchant_name', 'Unknown')}")
        print(f"{Fore.WHITE}\nDescription:\n{Fore.RED}{shop_data.get('description', 'No description available.')}{Fore.RESET}")
        print(print_bar("large", Fore.YELLOW))
        
        choice = select_option(["Yes", "No"], f"Would you like to enter {Fore.LIGHTBLUE_EX}{shop_name}{Fore.YELLOW}?{Fore.RESET}", Fore.YELLOW, False)
        
        if choice[0] == "Yes":
            shop = Shop(game_data, shop_name, shop_data)        
            shop.open_shop(player)
        if choice[0] == "No":
            time.sleep(1)
            clear_console()


def battle(player, enemy):
    """Enhanced battle system with equipment and abilities."""
    Tools.is_music_playing = False
    time.sleep(1)
    Tools.is_music_playing = True
    battle_music = threading.Thread(target=Audio.play_music, args=(os.path.join("music", "battle.wav"), 0.5))
    battle_music.start()
    player.state = "battle"

    while enemy.is_alive() and player.health > 0:
        if player.state == "flee":
            flee_chance = random.randint(1, 20) + player.modifiers['Dexterity']
            if flee_chance > 10:
                print(Fore.GREEN + f"\nYou successfully escaped with a roll of {Fore.CYAN}{flee_chance}{Fore.YELLOW}")
            else:
                print(Fore.GREEN + f"\nYou successfully escaped!!")
            input("Press Enter to continue...")
            Tools.is_music_playing = False
            time.sleep(1)
            Tools.is_music_playing = True
            music = threading.Thread(target=Audio.play_music, args=(os.path.join("music", "traveling.mp3"), 0.5))
            music.start()
            return

        player.ac = player.get_ac()
        player_ac = player.ac
        if player.equipped_armor:
            player_ac += player.equipped_armor.get('ac_bonus', 0)
            
        clear_console()
        print_titlebar(f"{Fore.BLUE}{player.name}{Fore.RESET}", color=Fore.YELLOW)
        print(f"{Fore.BLUE}   Armor Rating: {player.ac}{Fore.RESET}")
        print(f"{Fore.RED}   HP: ({player.health}/{player.max_health}){Fore.RESET}")

        print_titlebar(f"{Fore.RED}{enemy.name}{Fore.YELLOW}", color=Fore.YELLOW)
        print(f"   {Fore.RED}HP: {enemy.health}\n")

        options = ['Attack', 'Use Ability', 'Use Item', 'Flee']

        # Player's Turn
        print_titlebar("", color=Fore.YELLOW)
        action, _ = select_option(options, "Choose your action:", clear_screen=False, player_send=player)
        
        if action == 'Attack':
            clear_console()
            print_titlebar(f"{Fore.CYAN}{player.name.upper()} TURN{Fore.YELLOW}", color=Fore.YELLOW)
            attack_roll = random.randint(1, 20) + player.modifiers['Strength']
            if player.equipped_weapon:
                attack_roll += player.equipped_weapon.get('attack_bonus', 0)
            time.sleep(1)
            print(f"\nYou rolled an attack of {Fore.GREEN}{attack_roll}{Fore.RESET} vs {Fore.RED}{enemy.name}'s{Fore.BLUE} Armor Rating {enemy.ac}{Fore.RESET}")
            if attack_roll >= enemy.ac:
                damage_roll = player.equipped_weapon.get('damage', '1d4') if player.equipped_weapon else '1d4'
                damage = roll_damage(damage_roll) + player.modifiers['Strength']
                enemy.health -= damage
                time.sleep(1)
                print(f"{Fore.RESET}{player.name} {Fore.GREEN}HITS{Fore.RESET} the {Fore.RED}{enemy.name} for {Fore.RED}{damage} damage!{Fore.RESET}")
            else:
                time.sleep(1)
                print(Fore.RED + "Your attack missed!")
                
        elif action == 'Use Ability':
            clear_console()
            use_ability(player, enemy)
        elif action == 'Use Item':
            clear_console()
            player.show_inventory_table()
        elif action == 'Flee':
            flee_chance = random.randint(1, 20) + player.modifiers['Dexterity']
            if flee_chance > 10:
                player.state = "flee"
            else:
                print(Fore.RED + f"\nYou failed to escape with a roll of {Fore.CYAN}{flee_chance}{Fore.RESET}")

        # Enemy's turn
        if enemy.is_alive():
            print()
            time.sleep(1)
            print_titlebar(f"{Fore.RED}{enemy.name.upper()} TURN{Fore.YELLOW}", color=Fore.YELLOW)
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
    
    # Defeated Enemy
    if not enemy.is_alive():
        time.sleep(2)
        print(Fore.GREEN + f"You defeated the {enemy.name}!")
        earned_exp = enemy.level * 10
        enemy_gold_loot = int(enemy.gold * random.uniform(0.33, 1.5))
        player.exp += earned_exp
        player.gold += enemy_gold_loot
        print(Fore.YELLOW + f"You gained {earned_exp} experience and found {enemy_gold_loot} gold!")
        Tools.is_music_playing = False
        time.sleep(1)
        Tools.is_music_playing = True
        music = threading.Thread(target=Audio.play_music, args=(os.path.join("music", "traveling.mp3"), 0.5))
        music.start()
        input("Press Enter to continue...")


def use_ability(player, enemy):
    """Handle ability usage in battle."""
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
    """Parse damage strings like '2d6' and return the total damage."""
    num, die = damage_str.split('d')
    total = sum(random.randint(1, int(die)) for _ in range(int(num)))
    return total


def print_bar(size, color=Fore.WHITE, style=Style.NORMAL):
    """Print a decorative bar."""
    if size == "small":
        return f"{color}════════════════════════════{Fore.RESET}"
    elif size == "normal":
        return f"{color}════════════════════════════════════════════{Fore.RESET}"
    elif size == "large":
        return f"{color}════════════════════════════════════════════════════════{Fore.RESET}"


def create_character(game_data):
    """Character creation process."""
    color = Fore.GREEN
    reset = Fore.RESET
    input_color = Fore.CYAN

    # Gender selection
    gender_options = ["Male", "Female", "Non-binary"]
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
    clear_console()
    
    lore_choice = input("Would you like some lore? (y/n): ")
    if lore_choice.lower() == "y":
        Tools.tell_story("creation", "the_creation.mp3", 4, 3)
    
    # Play Travel Music
    Tools.is_music_playing = False
    time.sleep(1)
    Tools.is_music_playing = True
    travel_music = threading.Thread(target=Audio.play_music, args=(os.path.join("music", "traveling.mp3"),))
    travel_music.start()
    
    return player


def display_title_screen(game_data):
    """Display the game title screen."""
    if game_data.settings.get('Title SFX Enabled', False):
        sfx_thread = threading.Thread(target=Audio.play_sfx, args=(os.path.join("sfx", "title.mp3"), 2))
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
