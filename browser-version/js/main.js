// Main initialization script for Legends of the Realm
(function() {
    'use strict';

    // Game version and metadata - will be loaded from gameinfo.json
    let GAME_VERSION = 'a0.14.0';
    let GAME_DEVELOPER = 'Scotty Venable';
    let GAME_YEAR = '2024';

    // Load game info from JSON file
    async function loadGameInfo() {
        try {
            const response = await fetch('data/gameinfo.json');
            const gameInfo = await response.json();
            
            GAME_VERSION = gameInfo.Version;
            GAME_DEVELOPER = gameInfo.Developer;
            GAME_YEAR = gameInfo.CopyrightYear;
            
            console.log(`Game info loaded: ${gameInfo.Name} v${GAME_VERSION} by ${GAME_DEVELOPER}`);
        } catch (error) {
            console.warn('Failed to load game info, using defaults:', error);
        }
    }

    // Initialize game when DOM is loaded
    document.addEventListener('DOMContentLoaded', async function() {
        console.log('Legends of the Realm - Starting initialization...');
        
        try {
            // Load game info first
            await loadGameInfo();
            
            console.log(`Legends of the Realm v${GAME_VERSION} - Main script loaded`);
            console.log(`Legends of the Realm v${GAME_VERSION} - Starting initialization...`);
            
            // Update version info in UI
            updateVersionInfo();
            
            // Initialize UI manager
            window.uiManager.init();
            console.log('UI Manager initialized');
            
            // Initialize game engine
            await window.gameEngine.init();
            console.log('Game initialization complete!');
            
            // Start title music immediately (before user interaction)
            if (window.audioManager && window.audioManager.isInitialized) {
                // Try to play title music immediately
                window.audioManager.playMusic('title');
            }
            
            // Enable audio context on first user interaction
            setupAudioContextEnabler();
            
            // Setup error handling
            setupErrorHandling();
            
            // Setup fullscreen functionality
            setupFullscreenSupport();
            
            // Check browser compatibility
            checkBrowserCompatibility();
            
            // Enable developer mode for testing
            if (isDevelopmentMode()) {
                window.developerTools.enable();
                console.log('Development mode enabled');
                console.log('Development tools available via window.dev object');
            }
            
        } catch (error) {
            console.error('Failed to initialize game:', error);
            showInitializationError(error);
        }
    });

    // Update version information in the UI
    function updateVersionInfo() {
        const versionElement = document.getElementById('game-version');
        const developerElement = document.getElementById('game-developer');
        const yearElement = document.getElementById('game-year');

        if (versionElement) versionElement.textContent = GAME_VERSION;
        if (developerElement) developerElement.textContent = GAME_DEVELOPER;
        if (yearElement) yearElement.textContent = GAME_YEAR;
    }

    // Setup audio context enabler for autoplay restrictions
    function setupAudioContextEnabler() {
        const enableAudio = () => {
            if (window.audioManager) {
                window.audioManager.enableAudioContext();
                // Ensure title music is playing after user interaction
                if (window.gameEngine && window.gameEngine.gameState === 'title') {
                    window.audioManager.playMusic('title');
                }
            }
            // Remove event listeners after first interaction
            document.removeEventListener('click', enableAudio);
            document.removeEventListener('keydown', enableAudio);
            document.removeEventListener('touchstart', enableAudio);
        };

        // Add event listeners for user interaction
        document.addEventListener('click', enableAudio);
        document.addEventListener('keydown', enableAudio);
        document.addEventListener('touchstart', enableAudio);
    }

    // Setup global error handling
    function setupErrorHandling() {
        // Handle uncaught JavaScript errors
        window.addEventListener('error', function(event) {
            console.error('Uncaught error:', event.error);
            
            // Don't show error dialog for minor issues
            if (event.error && event.error.name !== 'NetworkError') {
                showGameError('An unexpected error occurred. The game may not function properly.');
            }
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            console.error('Unhandled promise rejection:', event.reason);
            
            // Prevent default browser behavior
            event.preventDefault();
            
            showGameError('A network or loading error occurred. Please check your connection and try again.');
        });
    }

    // Setup fullscreen functionality
    function setupFullscreenSupport() {
        // Add fullscreen toggle function to window
        window.toggleFullscreen = function() {
            if (!document.fullscreenElement) {
                // Enter fullscreen
                const element = document.documentElement;
                if (element.requestFullscreen) {
                    element.requestFullscreen();
                } else if (element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if (element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }
            } else {
                // Exit fullscreen
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen();
                }
            }
        };

        // Auto-enter fullscreen when starting a new game
        window.enterFullscreenOnGameStart = function() {
            if (!document.fullscreenElement) {
                setTimeout(() => {
                    window.toggleFullscreen();
                }, 100);
            }
        };

        // Listen for fullscreen changes
        document.addEventListener('fullscreenchange', updateFullscreenButton);
        document.addEventListener('webkitfullscreenchange', updateFullscreenButton);
        document.addEventListener('msfullscreenchange', updateFullscreenButton);

        // Add F11 key listener for fullscreen toggle
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F11') {
                e.preventDefault();
                window.toggleFullscreen();
            }
            
            // Add ESC key listener for pause menu
            if (e.key === 'Escape') {
                e.preventDefault();
                if (window.gameEngine && window.gameEngine.gameState === 'playing') {
                    if (isPaused()) {
                        resumeGame();
                    } else {
                        pauseGame();
                    }
                }
            }
        });
    }

    // Update fullscreen button text
    function updateFullscreenButton() {
        const fullscreenBtn = document.getElementById('fullscreen-toggle');
        if (fullscreenBtn) {
            fullscreenBtn.textContent = document.fullscreenElement ? 'Exit Fullscreen' : 'Fullscreen';
        }
    }

    // Check if we're in development mode
    function isDevelopmentMode() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.search.includes('dev=true');
    }

    // Add browser compatibility check
    function checkBrowserCompatibility() {
        const requiredFeatures = [
            'fetch',
            'localStorage',
            'Promise',
            'JSON'
        ];

        const missingFeatures = requiredFeatures.filter(feature => !window[feature]);
        
        if (missingFeatures.length > 0) {
            console.warn('Missing browser features:', missingFeatures);
            showGameError(`Your browser may not be fully compatible. Missing: ${missingFeatures.join(', ')}`);
        }
    }

    // Show initialization error
    function showInitializationError(error) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(45deg, #8b0000, #a00000);
            color: white;
            padding: 30px;
            border-radius: 12px;
            border: 3px solid #ff0000;
            z-index: 10000;
            text-align: center;
            font-family: 'Cinzel', serif;
            max-width: 500px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
        `;
        errorDiv.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: #ffcccc; font-size: 1.5rem;">⚠️ Game Initialization Error</h3>
            <p style="margin: 0 0 20px 0; line-height: 1.4;">${error.message}</p>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button onclick="window.location.reload()" style="
                    background: linear-gradient(45deg, #8b4513, #a0522d);
                    border: 2px solid #d4af37;
                    color: #e8d5b7;
                    padding: 12px 24px;
                    font-family: 'Cinzel', serif;
                    font-size: 16px;
                    cursor: pointer;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                ">Reload Game</button>
                <button onclick="console.log('Error details:', ${JSON.stringify(error.stack)})" style="
                    background: linear-gradient(45deg, #654321, #8b4513);
                    border: 2px solid #8b4513;
                    color: #e8d5b7;
                    padding: 12px 24px;
                    font-family: 'Cinzel', serif;
                    font-size: 16px;
                    cursor: pointer;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                ">Show Details</button>
            </div>
        `;
        document.body.appendChild(errorDiv);
    }

    // Show general game error
    function showGameError(message) {
        // Only show if no error is currently displayed
        if (document.querySelector('.game-error')) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'game-error';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(139, 0, 0, 0.95);
            color: #ffcccc;
            padding: 15px 20px;
            border-radius: 8px;
            border: 2px solid #ff0000;
            z-index: 9999;
            font-family: 'Cinzel', serif;
            max-width: 400px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            animation: slideDown 0.3s ease-out;
        `;

        errorDiv.innerHTML = `
            <div style="margin-bottom: 10px;">⚠️ ${message}</div>
            <button onclick="this.parentElement.remove()" style="
                background: #660000;
                color: white;
                border: 1px solid #ff0000;
                padding: 5px 10px;
                cursor: pointer;
                border-radius: 3px;
                font-family: 'Cinzel', serif;
                font-size: 12px;
            ">Dismiss</button>
        `;

        document.body.appendChild(errorDiv);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 10000);
    }

    // Add slideDown animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from {
                transform: translate(-50%, -100%);
                opacity: 0;
            }
            to {
                transform: translate(-50%, 0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);

    // Expose version info globally
    window.GAME_INFO = {
        get version() { return GAME_VERSION; },
        get developer() { return GAME_DEVELOPER; },
        get year() { return GAME_YEAR; }
    };

    // Pause Game Functions
    window.pauseGame = function() {
        if (window.gameEngine && window.gameEngine.gameState === 'playing') {
            const pauseOverlay = document.getElementById('pause-overlay');
            if (pauseOverlay) {
                pauseOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
                
                // Pause audio
                if (window.audioManager && window.audioManager.backgroundMusicElement) {
                    window.audioManager.backgroundMusicElement.pause();
                }
                
                console.log('Game paused');
            }
        }
    };

    window.resumeGame = function() {
        const pauseOverlay = document.getElementById('pause-overlay');
        if (pauseOverlay) {
            pauseOverlay.classList.remove('active');
            document.body.style.overflow = '';
            
            // Resume audio
            if (window.audioManager && window.audioManager.backgroundMusicElement && window.audioManager.musicEnabled) {
                window.audioManager.backgroundMusicElement.play().catch(e => console.log('Music resume prevented'));
            }
            
            console.log('Game resumed');
        }
    };

    window.isPaused = function() {
        const pauseOverlay = document.getElementById('pause-overlay');
        return pauseOverlay && pauseOverlay.classList.contains('active');
    };

    window.showPauseSettings = function() {
        // Show settings but keep pause menu open
        window.gameEngine.showSettings();
    };

    window.showPauseMessage = function(message) {
        const statusElement = document.getElementById('pause-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.style.color = '#90ee90';
            
            // Clear message after 3 seconds
            setTimeout(() => {
                statusElement.textContent = '';
            }, 3000);
        }
    };

    window.confirmReturnToTitle = function() {
        if (confirm('Are you sure you want to return to the title screen? Any unsaved progress will be lost.')) {
            resumeGame(); // Close pause menu first
            setTimeout(() => {
                window.gameEngine.showTitleScreen();
            }, 100);
        }
    };

    console.log('Legends of the Realm - Main script loaded');

})();
