"""
Enemy class for combat encounters.
"""


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
        """Check if the enemy is still alive."""
        return self.health > 0
