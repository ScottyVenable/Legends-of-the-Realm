"""
Item class for in-game items, weapons, armor, and consumables.
"""


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
