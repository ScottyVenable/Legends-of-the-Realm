#!/usr/bin/env python3
"""
Quick test script to verify the shop system is working correctly
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import GameData, Shop, Character, select_option, Game

def test_shop():
    """Test the shop system directly"""
    print("Testing Shop System...")
    
    # Initialize game data
    game_data = GameData()
    
    # Check if shop data exists
    print(f"Available shops: {list(game_data.shops.keys())}")
    
    # Test Bugbee's shop specifically
    shop_name = "Bugbee's Blades & Brews"
    if shop_name in game_data.shops:
        print(f"\n✓ Found shop: {shop_name}")
        shop_data = game_data.shops[shop_name]
        print(f"✓ Shop data: {shop_data}")
        
        # Create a test character
        test_character = Character(
            name="Test Hero", 
            race=game_data.races["Human"], 
            background="Soldier",
            char_class="Fighter",  # Pass class name, not the class dict
            gender="Male"
        )
        test_character.gold = 1000  # Give some gold for testing
        
        # Test shop summary
        print(f"\n--- Testing shop_summary ---")
        try:
            Game.shop_summary(shop_name, test_character, game_data)
            print("✓ shop_summary executed successfully")
        except Exception as e:
            print(f"✗ shop_summary failed: {e}")
            
        # Test shop creation
        print(f"\n--- Testing Shop creation ---")
        try:
            shop = Shop(game_data, shop_name, shop_data)
            print(f"✓ Shop created successfully: {shop.shop_name}")
            print(f"✓ Shop items loaded: {len(shop.items)} items")
            for item in shop.items:
                print(f"  - {item.name}: {item.price} gold")
        except Exception as e:
            print(f"✗ Shop creation failed: {e}")
            
    else:
        print(f"✗ Shop '{shop_name}' not found!")
        
if __name__ == "__main__":
    test_shop()
