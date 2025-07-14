"""
Database utilities for managing game objects and relationships.
"""
from .database import GameData
from ..entities.npc import NPC
from ..systems.dialogue import Dialogue
from ..systems.shop import Shop


class Database:
    gamedata = GameData()
    NPCs = {}
    shops = []
    
    # Initialize NPCs with dialogue data
    for npc_name, npc_data in gamedata.npcs.items():
        # Create dialogue objects from JSON data
        npc_data['dialogues'] = [Dialogue(**dialogue_item) for dialogue_item in npc_data['dialogues']]
        NPCs[npc_name] = NPC(npc_name, npc_data['dialogues'])

    def create_shops_from_data(self):
        """Create shop instances from game data."""
        shops = []
        for shop_name, shop_data in self.gamedata.shops.items():
            shops.append(Shop(game_data=self.gamedata, shop_name=shop_name, shop_data=shop_data))
        return shops
