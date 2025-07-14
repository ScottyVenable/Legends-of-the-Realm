"""
Shop system for handling merchant interactions and item purchases.
"""
import os
import time
import random
import threading
from colorama import Fore
from ..ui.display import clear_console, print_titlebar
from ..entities.item import Item
from ..utils.tools import Tools

try:
    from prettytable import PrettyTable, SINGLE_BORDER
except ImportError:
    from ..utils.tools import PrettyTable, SINGLE_BORDER


class Shop:
    def __init__(self, game_data, shop_name, shop_data, npcs=None):
        self.gamedata = game_data
        self.shop_name = shop_name
        self.shop_data = shop_data
        self.items = []
        self.populate_inventory()
        self.npcs = npcs or []
        self.player = None

    @staticmethod
    def play_shop_sfx(shop_data, file_name="shop_greeting"):
        """
        Plays a sound effect for the given shop.

        Args:
            shop_data (dict): The dictionary containing shop data (including 'merchant_id').
            file_name (str, optional): The name of the sound file (without extension). 
                Defaults to "shop_greeting".
        """
        from ..audio.audio import Audio
        
        # Play Shop Greeting
        sfx_path = os.path.join("sfx", "voiceover", shop_data['merchant_id'], f"{file_name}.wav")
        if os.path.exists(sfx_path):
            Audio.play_sfx(sfx_path)

    def open_shop(self, player):
        """Open the shop interface for the player."""
        self.player = player
        
        # Add shop NPCs
        if hasattr(self.gamedata, 'npcs'):
            bugbee_npc = self.gamedata.npcs.get("Clement Bugbee")
            if bugbee_npc:
                self.npcs.append(bugbee_npc)
        
        self.merchant_name = self.shop_data['merchant_name']
        self.merchant_greeting = self.shop_data['merchant_greeting']
        self.merchant_goodbye = self.shop_data['merchant_goodbye']
        self.shop_type = self.shop_data['type']
        self.play_shop_music()
        self.play_shop_sfx(self.shop_data, "shop_greeting")

        # Shop Loop
        while True:
            clear_console()
            
            print_titlebar(f"{Fore.WHITE}Welcome to {Fore.BLUE}{self.shop_name}{Fore.YELLOW}!", color=Fore.YELLOW)
            print(f"\n{Fore.BLUE}{self.merchant_name}: {Fore.WHITE}{self.merchant_greeting}{Fore.RESET}\n")
            
            self.show_shop_inventory()

            print(f"{Fore.WHITE}Press {Fore.YELLOW}'{len(self.items) + 1}'{Fore.WHITE} to {Fore.RED}Exit shop{Fore.RESET}")
            print(f"{Fore.WHITE}Press {Fore.YELLOW}'{len(self.items) + 2}'{Fore.WHITE} to {Fore.CYAN}Open Inventory{Fore.RESET}")
            
            choice = input("\nWhat would you like to buy? Enter the item number: ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(self.items):
                    item = self.items[choice - 1]
                    item_price = item.price
                    if self.shop_data['inventory'][item.name]['on_sale']:
                        item_price = item.price - (item.price * (self.shop_data['inventory'][item.name]['discount'] / 100))
                        item_price = int(item_price)
                    if player.gold >= item_price:
                        if self.shop_data['inventory'][item.name]['quantity'] > 0:
                            player.gold -= item_price
                            player.inventory.append(vars(item))
                            self.shop_data['inventory'][item.name]['quantity'] -= 1
                            print(Fore.GREEN + f"\nYou purchased {item.name}!")
                            purchase_sfx_count = self.get_purchase_sfx_count(self.shop_data['merchant_id'])
                            random_sfx_number = random.randint(1, purchase_sfx_count)
                            
                            from ..audio.audio import Audio
                            Audio.play_sfx(os.path.join("sfx", "voiceover", self.shop_data['merchant_id'], f"purchase - {random_sfx_number}.wav"))
                            time.sleep(1)
                            print(Fore.WHITE + f"You now have {Fore.YELLOW}[ {player.gold} ] {Fore.WHITE}gold.\n")
                            time.sleep(2)
                        else:
                            print(Fore.RED + f"\nSorry, {item.name} is out of stock.")
                            input("Press Enter to continue...")
                    else:
                        print(Fore.RED + "\nYou don't have enough gold.")
                        input("Press Enter to continue...")
                elif choice == len(self.items) + 1:
                    print(f"\n{Fore.BLUE}{self.merchant_name}: {Fore.WHITE}{self.merchant_goodbye}{Fore.RESET}")
                    self.play_shop_sfx(self.shop_data, "shop_goodbye")
                    Tools.is_music_playing = False
                    time.sleep(1)
                    Tools.is_music_playing = True
                    
                    from ..audio.audio import Audio
                    music_thread = threading.Thread(target=Audio.play_music, args=(Audio.traveling_music_path,))
                    music_thread.start()
                    time.sleep(2)
                    break
                elif choice == len(self.items) + 2:
                    self.show_player_info(self.player)
                else:
                    print(Fore.RED + "Invalid option.")
                    time.sleep(1)
            else:
                print(Fore.RED + "Please enter a valid option.")
                time.sleep(1)

    def get_present_npcs(self):
        """Returns a list of NPCs whose location matches the shop's name."""
        present_npcs = []
        if hasattr(self.gamedata, 'npcs'):
            for npc_name, npc_data in self.gamedata.npcs.items():
                if self.shop_name in npc_data.get('locations', []):
                    present_npcs.append(npc_name)
        return present_npcs

    def show_shop_inventory(self):
        """Display the shop's inventory in a formatted table."""
        player = self.player
        if not player:
            print("No player found")
            return
            
        print_titlebar(f"{Fore.BLUE}Shop Inventory{Fore.YELLOW}", color=Fore.YELLOW)
        print(Fore.CYAN + f"\n  Your Gold: {Fore.YELLOW}[ {player.gold} ] {Fore.CYAN}\n")

        # Create PrettyTable
        table = PrettyTable()
        table.field_names = ["#", "Item", "Price", "Quantity"]
        if hasattr(table, 'align') and hasattr(table.align, '__setitem__'):
            table.align["Item"] = "l"
            table.align["Price"] = "l"
            table.align["Quantity"] = "c"
        if hasattr(table, 'set_style'):
            if SINGLE_BORDER:
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

        print(table)

    def show_player_info(self, player):
        """Show player inventory."""
        clear_console()
        print_titlebar("Player Inventory")
        player.show_inventory_table()

    def populate_inventory(self):
        """Populate shop inventory with items."""
        for item_name, item_data in self.shop_data['inventory'].items():
            item_data['name'] = item_name
            if hasattr(self.gamedata, 'items') and item_name in self.gamedata.items:
                item_data.update(self.gamedata.items[item_name])
                item = Item(item_data)
                self.items.append(item)

    @staticmethod
    def new(gamedata, shop_name, shop_data):
        """Create a new shop instance."""
        return Shop(gamedata, shop_name, shop_data)

    def play_shop_music(self):
        """Play background music for the shop."""
        Tools.is_music_playing = False
        time.sleep(1)
        Tools.is_music_playing = True
        music_file = os.path.join("music", f"{self.shop_type}.wav")
        
        from ..audio.audio import Audio
        music_thread = threading.Thread(target=Audio.play_music, args=(music_file.lower(),))
        music_thread.start()
        Tools.is_music_playing = True
        
    def get_purchase_sfx_count(self, merchant_id):
        """Gets the number of "purchase" sound files for a given merchant."""
        sfx_dir = os.path.join("sfx", "voiceover", merchant_id)
        try:
            purchase_files = [
                f for f in os.listdir(sfx_dir) if f.startswith("purchase -") and f.endswith(".wav")
            ]
            return len(purchase_files)
        except FileNotFoundError:
            return 0
