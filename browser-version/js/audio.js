// Audio management system for Legends of the Realm

class AudioManager {
    constructor() {
        this.audioContext = null;
        this.musicEnabled = true;
        this.sfxEnabled = true;
        this.volume = 0.5;
        this.currentMusic = null;
        this.musicTracks = {};
        this.sfxSounds = {};
        this.voiceLines = {};
        this.isInitialized = false;
        
        // Bind methods to preserve 'this' context
        this.enableAudioContext = this.enableAudioContext.bind(this);
        this.playMusic = this.playMusic.bind(this);
        this.playSFX = this.playSFX.bind(this);
        this.toggleMusic = this.toggleMusic.bind(this);
        this.toggleSFX = this.toggleSFX.bind(this);
        
        this.init();
    }

    // Initialize audio system
    init() {
        try {
            // Create audio context (will be activated on first user interaction)
            if (typeof AudioContext !== 'undefined') {
                this.audioContext = new AudioContext();
            } else if (typeof webkitAudioContext !== 'undefined') {
                this.audioContext = new webkitAudioContext();
            }

            // Wait for DOM to be ready before getting audio elements
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.setupAudioElements();
                });
            } else {
                this.setupAudioElements();
            }

            this.loadAudioAssets();
            this.isInitialized = true;
            console.log('Audio Manager initialized');
        } catch (error) {
            console.error('Failed to initialize audio:', error);
            this.isInitialized = false;
        }
    }

    // Setup audio elements
    setupAudioElements() {
        // Get background music element
        this.backgroundMusicElement = document.getElementById('background-music');
        this.sfxElement = document.getElementById('sfx-player');

        if (this.backgroundMusicElement) {
            this.backgroundMusicElement.volume = this.volume;
            this.backgroundMusicElement.addEventListener('ended', () => {
                // Loop music by restarting
                if (this.musicEnabled && this.currentMusic) {
                    this.backgroundMusicElement.currentTime = 0;
                    this.backgroundMusicElement.play().catch(e => console.log('Music autoplay prevented'));
                }
            });
        } else {
            console.warn('Background music element not found');
        }

        if (!this.sfxElement) {
            console.warn('SFX element not found');
        }
    }

    // Load audio assets
    loadAudioAssets() {
        // Define music tracks
        this.musicTracks = {
            title: 'audio/music/title.mp3',
            creation: 'audio/music/creation.mp3',
            traveling: 'audio/music/traveling.mp3',
            tavern: 'audio/music/tavern.mp3',
            blacksmith: 'audio/music/blacksmith.mp3',
            battle: 'audio/music/battle.mp3',
            gameOver: 'audio/music/gameover.mp3'
        };

        // Define SFX sounds
        this.sfxSounds = {
            click: 'audio/sfx/click.wav',
            newGame: 'audio/sfx/newgame.wav',
            purchase: 'audio/sfx/purchase.wav',
            error: 'audio/sfx/error.wav'
        };

        // Define voice lines
        this.voiceLines = {
            blacksmith: {
                greeting: 'audio/voice/blacksmith_greeting.mp3',
                purchase: 'audio/voice/blacksmith_purchase.mp3',
                goodbye: 'audio/voice/blacksmith_goodbye.mp3'
            }
        };
    }

    // Enable audio context on user interaction
    enableAudioContext() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume().then(() => {
                console.log('Audio context resumed');
            }).catch(error => {
                console.error('Failed to resume audio context:', error);
            });
        }
    }

    // Play background music
    playMusic(trackName) {
        if (!this.isInitialized || !this.musicEnabled) return;

        try {
            const trackPath = this.musicTracks[trackName];
            if (!trackPath) {
                console.warn(`Music track '${trackName}' not found`);
                return;
            }

            // Only change if it's a different track
            if (this.currentMusic === trackName) return;

            if (this.backgroundMusicElement) {
                // Stop current music
                this.backgroundMusicElement.pause();
                this.backgroundMusicElement.currentTime = 0;

                // Set new source
                this.backgroundMusicElement.src = trackPath;
                this.currentMusic = trackName;

                // Play new music
                const playPromise = this.backgroundMusicElement.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.log('Music autoplay prevented:', error);
                        // Autoplay was prevented, user interaction needed
                    });
                }
            }
        } catch (error) {
            console.error('Error playing music:', error);
        }
    }

    // Play sound effect
    playSFX(soundName) {
        if (!this.isInitialized || !this.sfxEnabled) return;

        try {
            const soundPath = this.sfxSounds[soundName];
            if (!soundPath) {
                console.warn(`SFX '${soundName}' not found`);
                return;
            }

            if (this.sfxElement) {
                this.sfxElement.src = soundPath;
                this.sfxElement.volume = this.volume;
                
                const playPromise = this.sfxElement.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.log('SFX autoplay prevented:', error);
                    });
                }
            }
        } catch (error) {
            console.error('Error playing SFX:', error);
        }
    }

    // Play voice line
    playVoiceLine(character, lineName) {
        if (!this.isInitialized || !this.sfxEnabled) return;

        try {
            const voiceData = this.voiceLines[character];
            if (!voiceData || !voiceData[lineName]) {
                console.warn(`Voice line '${character}.${lineName}' not found`);
                return;
            }

            // Create temporary audio element for voice lines
            const voiceAudio = new Audio(voiceData[lineName]);
            voiceAudio.volume = this.volume;
            
            const playPromise = voiceAudio.play();
            if (playPromise !== undefined) {
                playPromise.catch(error => {
                    console.log('Voice line autoplay prevented:', error);
                });
            }
        } catch (error) {
            console.error('Error playing voice line:', error);
        }
    }

    // Toggle music on/off
    toggleMusic() {
        this.musicEnabled = !this.musicEnabled;
        
        if (this.backgroundMusicElement) {
            if (this.musicEnabled) {
                if (this.currentMusic) {
                    this.backgroundMusicElement.play().catch(e => console.log('Music play prevented'));
                }
            } else {
                this.backgroundMusicElement.pause();
            }
        }
        
        return this.musicEnabled;
    }

    // Toggle SFX on/off
    toggleSFX() {
        this.sfxEnabled = !this.sfxEnabled;
        return this.sfxEnabled;
    }

    // Set master volume (fixed method name)
    setMasterVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        
        if (this.backgroundMusicElement) {
            this.backgroundMusicElement.volume = this.volume;
        }
        
        if (this.sfxElement) {
            this.sfxElement.volume = this.volume;
        }
    }

    // Check if music is enabled
    isMusicEnabled() {
        return this.musicEnabled;
    }

    // Check if SFX is enabled
    isSFXEnabled() {
        return this.sfxEnabled;
    }

    // Get current volume
    getVolume() {
        return this.volume;
    }

    // Stop all audio
    stopAll() {
        if (this.backgroundMusicElement) {
            this.backgroundMusicElement.pause();
            this.backgroundMusicElement.currentTime = 0;
        }
        
        if (this.sfxElement) {
            this.sfxElement.pause();
            this.sfxElement.currentTime = 0;
        }
        
        this.currentMusic = null;
    }

    // Fade out current music
    fadeOut(duration = 1000) {
        if (!this.backgroundMusicElement || !this.musicEnabled) return;

        const startVolume = this.backgroundMusicElement.volume;
        const fadeStep = startVolume / (duration / 50);
        
        const fadeInterval = setInterval(() => {
            if (this.backgroundMusicElement.volume > fadeStep) {
                this.backgroundMusicElement.volume -= fadeStep;
            } else {
                this.backgroundMusicElement.volume = 0;
                this.backgroundMusicElement.pause();
                clearInterval(fadeInterval);
                // Restore volume for next track
                this.backgroundMusicElement.volume = this.volume;
            }
        }, 50);
    }

    // Fade in music
    fadeIn(trackName, duration = 1000) {
        if (!this.musicEnabled) return;

        this.playMusic(trackName);
        
        if (this.backgroundMusicElement) {
            this.backgroundMusicElement.volume = 0;
            
            const targetVolume = this.volume;
            const fadeStep = targetVolume / (duration / 50);
            
            const fadeInterval = setInterval(() => {
                if (this.backgroundMusicElement.volume < targetVolume - fadeStep) {
                    this.backgroundMusicElement.volume += fadeStep;
                } else {
                    this.backgroundMusicElement.volume = targetVolume;
                    clearInterval(fadeInterval);
                }
            }, 50);
        }
    }

    // Preload audio assets
    preloadAudio() {
        // Preload critical audio files
        const criticalTracks = ['title', 'traveling', 'battle'];
        
        criticalTracks.forEach(trackName => {
            const trackPath = this.musicTracks[trackName];
            if (trackPath) {
                const audio = new Audio();
                audio.preload = 'auto';
                audio.src = trackPath;
            }
        });
    }
}

// Create global audio manager instance
window.audioManager = new AudioManager();

// Global functions for HTML onclick handlers (updated to match function names)
function toggleMusic() {
    if (window.audioManager) {
        const musicBtn = document.getElementById('music-toggle');
        const isPlaying = window.audioManager.toggleMusic();
        if (musicBtn) {
            musicBtn.textContent = isPlaying ? 'Music: ON' : 'Music: OFF';
        }
        
        // Update settings modal button if open
        const settingsBtn = document.getElementById('settings-music-toggle');
        if (settingsBtn) {
            settingsBtn.textContent = isPlaying ? 'ON' : 'OFF';
        }
    }
}

function toggleSFX() {
    if (window.audioManager) {
        const sfxBtn = document.getElementById('sfx-toggle');
        const isEnabled = window.audioManager.toggleSFX();
        if (sfxBtn) {
            sfxBtn.textContent = isEnabled ? 'SFX: ON' : 'SFX: OFF';
        }
        
        // Update settings modal button if open
        const settingsBtn = document.getElementById('settings-sfx-toggle');
        if (settingsBtn) {
            settingsBtn.textContent = isEnabled ? 'ON' : 'OFF';
        }
    }
}

function setVolume(value) {
    if (window.audioManager) {
        window.audioManager.setMasterVolume(value / 100);
    }
}
