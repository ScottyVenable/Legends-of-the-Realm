"""
NPC (Non-Player Character) class for handling dialogue and interactions.
"""
import time
from colorama import Fore
from ..ui.display import clear_console


class NPC:
    def __init__(self, name, dialogue_data):
        self.name = name
        self.dialogue = dialogue_data  # Assign the dialogue data to the dialogue attribute

    def talk(self, player, dialogue_id=0):
        """Handle dialogue interaction with the player."""
        if self.dialogue[dialogue_id]:
            current_dialogue = self.dialogue[dialogue_id]
            while current_dialogue:
                clear_console()
                print(Fore.BLUE + f"{self.name}: {Fore.RESET}{current_dialogue.text}\n")
                
                if current_dialogue.action:
                    if current_dialogue.action == "accept_quest_with_reward":
                        from ..systems.quest import Quest
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
            input("Press Enter to continue...")
        else:
            print(f"{Fore.RED} No dialogue found for ID: {dialogue_id}{Fore.RESET}")
            time.sleep(1)
