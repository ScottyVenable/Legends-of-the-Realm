"""
Audio system for managing music and sound effects.
"""
import os
import time
import threading
import pygame
from colorama import Fore
from ..utils.tools import Tools


class Audio:
    traveling_music_path = os.path.join("music", "traveling.mp3")
    tavern_music_path = os.path.join("music", "tavern.wav")
    
    @staticmethod
    def play_music(music_name, volume=0.3):
        """Play background music with looping."""
        if os.path.exists(music_name):
            pygame.mixer.init()
            pygame.mixer.music.load(music_name)
            pygame.mixer.music.play(-1)  # Loop the music
            pygame.mixer.music.set_volume(volume)  # Set volume
            while pygame.mixer.music.get_busy() and Tools.is_music_playing:
                time.sleep(1)  # Check periodically if music should stop
            pygame.mixer.music.stop()
        else:
            print(Fore.RED + f"Music file {music_name} not found.")

    @staticmethod
    def play_sfx(sfx_path, delay=0, volume=1.0):
        """Play a sound effect."""
        if os.path.exists(sfx_path):
            sound = pygame.mixer.Sound(sfx_path)
            time.sleep(delay)
            sound.play()
            sound.set_volume(volume)
        else:
            print(Fore.RED + f"Sound effect file {sfx_path} not found.")
