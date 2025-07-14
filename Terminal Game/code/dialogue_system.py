class DialogueManager:
    def __init__(self, npc_name, dialogue_data):
        self.npc_name = npc_name
        self.dialogue_data = dialogue_data  # Load dialogue data from the NPC's JSON file
        self.current_node = None  # Track the current node

    def start_dialogue(self, player):
        self.current_node = self.find_initial_node() 
        self.show_dialogue(player)

    def find_initial_node(self):
        # Find the appropriate starting node (based on conditions)
        # For example:
        for node in self.dialogue_data:
            if not node.condition: 
                return node
        return None

    def show_dialogue(self, player):
        if self.current_node:
            # Check conditions for the node
            if not self.current_node.condition or self.check_condition(self.current_node.condition, player): 
                clear_console()
                print(Fore.BLUE + f"{self.npc_name}: {Fore.RESET}{self.current_node.text}\n")

                # Show responses
                for idx, response in enumerate(self.current_node.responses):
                    print(f"{idx + 1}. {response['text']}")

                choice = input("\nEnter the number of your choice: ")
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.current_node.responses):
                        self.handle_response(self.current_node.responses[idx], player)
                    else:
                        print(Fore.RED + "Invalid choice.")
                else:
                    print(Fore.RED + "Invalid input. Please enter a number.")
            else:
                print(Fore.RED + "This dialogue is not available at this time.") 
        else:
            print(Fore.RED + "No dialogue found.")
        input("Press Enter to continue...")

    def handle_response(self, response, player):
        if response.get("next_id"):
            self.current_node = self.dialogue_data[response["next_id"]]
        if response.get("action"):
            self.execute_action(response["action"], player)

    def execute_action(self, action_name, player):
        if action_name == "accept_quest":
            # Add a quest to the player's quest list 
            # (You'll need to define a quest system)
            pass
        elif action_name == "give_gold":
            player.gold += 50 # Add 50 gold
            print(Fore.GREEN + "You received 50 gold!")
        # ... add more actions as needed ... 

    def check_condition(self, condition_name, player):
        # Implement condition checking
        # For example:
        if condition_name == "first_interaction":
            # Check if this is the first interaction
            if player.relationships.get(self.npc_name) is None:
                return True
        # ... add more conditions as needed ... 
        return False