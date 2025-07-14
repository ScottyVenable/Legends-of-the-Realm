"""
Quest system for managing quests and rewards.
"""
from colorama import Fore


class Quest:
    @staticmethod
    def accept_quest_with_reward(player, reward_amount):
        """Accept a quest and give the player a reward."""
        player.gold += reward_amount
        print(Fore.GREEN + f"You have accepted the quest and received {reward_amount} gold.")
        # TODO: Add quest tracking, status updates, etc.
