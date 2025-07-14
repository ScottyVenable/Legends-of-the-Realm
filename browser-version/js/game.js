// Main game engine and logic
class GameEngine {
    constructor() {
        this.gameState = 'title';
        this.currentLocation = null;
        this.gameLoaded = false;
        this.saveKey = 'legends_of_the_realm_save';
        
        // Time and day tracking
        this.gameDay = 1;
        this.dayStartTime = Date.now();
        this.shopSalesCache = {}; // Cache shop sales per day
        
        // Dialogue system
        this.currentDialogue = null;
        
        // Journal system - will be populated from data files
        this.journal = {
            rumors: [],
            quests: []
        };
        
        // Changelog data
        this.changelogData = {};
    }

    // Initialize the game
    async init() {
        console.log('Initializing Legends of the Realm...');
        
        // Show loading screen
        this.showLoadingScreen();
        
        try {
            // Load all game data
            const dataLoaded = await window.dataManager.loadAllData();
            if (!dataLoaded) {
                throw new Error('Failed to load game data');
            }

            // Initialize quest manager
            await window.questManager.init();

            // Load rumors and quests from data files
            await this.loadJournalData();

            // Load changelog data
            await this.loadChangelogData();
            
            // Initialize quest manager reference
            this.questManager = window.questManager;

            // Initialize audio and start title music
            if (window.audioManager && window.audioManager.isInitialized) {
                window.audioManager.playMusic('title');
            }

            // Hide loading screen
            this.hideLoadingScreen();

            // Show title screen
            this.showTitleScreen();

            this.gameLoaded = true;
            console.log('Game initialized successfully');

        } catch (error) {
            console.error('Failed to initialize game:', error);
            this.hideLoadingScreen();
            this.showError('Failed to initialize game. Please refresh the page.');
        }
    }

    // Load rumors and quests from data files
    async loadJournalData() {
        try {
            // Load rumors
            const rumorsResponse = await fetch('data/rumors.json');
            const rumorsData = await rumorsResponse.json();
            
            // Add heard rumors to journal
            Object.values(rumorsData).forEach(rumor => {
                if (rumor.heard) {
                    this.journal.rumors.push({
                        id: rumor.id,
                        title: rumor.title,
                        content: rumor.content,
                        discovered: true,
                        location: rumor.location
                    });
                }
            });

            // Load quests
            const questsResponse = await fetch('data/quests.json');
            const questsData = await questsResponse.json();
            
            // Add available quests to journal
            Object.values(questsData).forEach(quest => {
                if (quest.available) {
                    this.journal.quests.push({
                        id: quest.id,
                        title: quest.title,
                        description: quest.description,
                        objective: quest.objective,
                        status: quest.status,
                        location: quest.location,
                        reward: quest.reward
                    });
                }
            });

            console.log('Journal data loaded successfully');
        } catch (error) {
            console.error('Failed to load journal data:', error);
            // Fall back to default data if files can't be loaded
            this.journal = {
                rumors: [
                    {
                        id: 'forest_lights',
                        title: 'Strange Lights in the Forest',
                        content: 'I heard from the tavern keeper that strange lights were seen over the Dark Forest last night. The locals seem uneasy about it.',
                        discovered: true,
                        location: 'Village of Millhaven'
                    }
                ],
                quests: [
                    {
                        id: 'missing_merchant',
                        title: 'The Missing Merchant',
                        description: 'I need to investigate the overdue caravan on the forest road.',
                        objective: 'Investigate the overdue caravan',
                        status: 'active',
                        location: 'Forest Road',
                        reward: '50 gold, experience'
                    }
                ]
            };
        }
    }

    // Load changelog data from JSON file
    async loadChangelogData() {
        try {
            const response = await fetch('data/gamechanges.json');
            this.changelogData = await response.json();
            console.log('Changelog data loaded successfully');
        } catch (error) {
            console.error('Failed to load changelog data:', error);
            this.changelogData = {};
        }
    }

    // Show loading screen
    showLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.add('active');
        }
    }

    // Hide loading screen
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.remove('active');
        }
    }

    // Show title screen
    showTitleScreen() {
        this.gameState = 'title';
        this.switchScreen('title-screen');
        
        // Always play title music when showing title screen
        if (window.audioManager && window.audioManager.isInitialized) {
            console.log('Starting title music...');
            window.audioManager.playMusic('title');
        }
    }

    // Switch between different game screens
    switchScreen(screenId) {
        // Hide all screens
        const screens = document.querySelectorAll('.screen');
        screens.forEach(screen => {
            screen.classList.remove('active');
        });

        // Show the requested screen
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
        } else {
            console.error(`Screen ${screenId} not found`);
        }
    }

    // Start new game
    startNewGame() {
        if (window.audioManager) {
            window.audioManager.playSFX('newGame');
        }
        this.gameState = 'character-creation';
        this.setupCharacterCreation();
        this.switchScreen('character-creation');
        if (window.audioManager) {
            window.audioManager.playMusic('creation');
        }
        
        // Enter fullscreen for immersive experience
        if (window.enterFullscreenOnGameStart) {
            window.enterFullscreenOnGameStart();
        }
    }

    // Setup character creation screen
    setupCharacterCreation() {
        // Populate race dropdown
        const raceSelect = document.getElementById('race-select');
        if (raceSelect) {
            const races = window.dataManager.getAllRaces();
            raceSelect.innerHTML = '<option value="">Choose your race...</option>';
            races.forEach(race => {
                const option = document.createElement('option');
                option.value = race;
                option.textContent = race;
                raceSelect.appendChild(option);
            });

            raceSelect.addEventListener('change', (e) => {
                const raceData = window.dataManager.getRace(e.target.value);
                const description = document.getElementById('race-description');
                if (description && raceData) {
                    let content = raceData.description || 'No description available.';
                    
                    // Add attribute bonuses info
                    if (raceData.AbilityScoreImprovements) {
                        content += '\n\nAttribute Bonuses: ';
                        const bonuses = [];
                        for (const [attr, bonus] of Object.entries(raceData.AbilityScoreImprovements)) {
                            if (bonus > 0) {
                                bonuses.push(`${attr} +${bonus}`);
                            }
                        }
                        content += bonuses.join(', ');
                    }
                    
                    description.textContent = content;
                }
                this.checkCharacterFormCompletion();
            });
        }

        // Populate class dropdown
        const classSelect = document.getElementById('class-select');
        if (classSelect) {
            const classes = window.dataManager.getAllClasses();
            classSelect.innerHTML = '<option value="">Choose your class...</option>';
            classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls;
                option.textContent = cls;
                classSelect.appendChild(option);
            });

            classSelect.addEventListener('change', (e) => {
                const classData = window.dataManager.getClass(e.target.value);
                const description = document.getElementById('class-description');
                if (description && classData) {
                    let content = classData.description || 'No description available.';
                    
                    // Add abilities info
                    if (classData.abilities) {
                        content += '\n\nSpecial Abilities: ';
                        const abilities = Object.keys(classData.abilities);
                        if (abilities.length > 0) {
                            content += abilities.join(', ');
                        }
                    }
                    
                    description.textContent = content;
                }
                this.checkCharacterFormCompletion();
            });
        }

        // Populate background dropdown
        const backgroundSelect = document.getElementById('background-select');
        if (backgroundSelect) {
            const backgrounds = window.dataManager.getAllBackgrounds();
            backgroundSelect.innerHTML = '<option value="">Choose your background...</option>';
            backgrounds.forEach(bg => {
                const option = document.createElement('option');
                option.value = bg;
                option.textContent = bg;
                backgroundSelect.appendChild(option);
            });

            backgroundSelect.addEventListener('change', (e) => {
                const bgData = window.dataManager.getBackground(e.target.value);
                const description = document.getElementById('background-description');
                if (description && bgData) {
                    description.textContent = bgData.description || 'No description available.';
                }
                this.checkCharacterFormCompletion();
            });
        }

        // Setup attribute method switching
        const statMethodRadios = document.querySelectorAll('input[name="stat-method"]');
        statMethodRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const rolledDiv = document.getElementById('rolled-attributes');
                const pointbuyDiv = document.getElementById('pointbuy-attributes');
                
                if (e.target.value === 'pointbuy') {
                    rolledDiv.style.display = 'none';
                    pointbuyDiv.style.display = 'block';
                    CharacterCreator.setupPointBuy();
                } else {
                    rolledDiv.style.display = 'block';
                    pointbuyDiv.style.display = 'none';
                }
            });
        });

        // Setup form change listeners
        const nameInput = document.getElementById('character-name');
        const genderRadios = document.querySelectorAll('input[name="gender"]');
        
        if (nameInput) {
            nameInput.addEventListener('input', this.checkCharacterFormCompletion.bind(this));
        }
        
        genderRadios.forEach(radio => {
            radio.addEventListener('change', this.checkCharacterFormCompletion.bind(this));
        });
    }

    // Roll attributes for character creation
    rollAttributes() {
        const rollStat = () => {
            // Roll 4d6, drop lowest
            const rolls = [];
            for (let i = 0; i < 4; i++) {
                rolls.push(Math.floor(Math.random() * 6) + 1);
            }
            rolls.sort((a, b) => b - a);
            return rolls[0] + rolls[1] + rolls[2]; // Sum of highest 3
        };

        const attributes = {
            strength: rollStat(),
            dexterity: rollStat(),
            constitution: rollStat(),
            intelligence: rollStat(),
            wisdom: rollStat(),
            charisma: rollStat()
        };

        // Display the rolled attributes
        const resultDiv = document.getElementById('attribute-results');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="rolled-stats">
                    <h4>Your Rolled Stats:</h4>
                    <div class="stat-grid">
                        <div class="stat-item">Strength: <span class="stat-value">${attributes.strength}</span></div>
                        <div class="stat-item">Dexterity: <span class="stat-value">${attributes.dexterity}</span></div>
                        <div class="stat-item">Constitution: <span class="stat-value">${attributes.constitution}</span></div>
                        <div class="stat-item">Intelligence: <span class="stat-value">${attributes.intelligence}</span></div>
                        <div class="stat-item">Wisdom: <span class="stat-value">${attributes.wisdom}</span></div>
                        <div class="stat-item">Charisma: <span class="stat-value">${attributes.charisma}</span></div>
                    </div>
                    <button onclick="gameEngine.rollAttributes()" class="reroll-btn">Reroll</button>
                </div>
            `;
        }

        // Store the attributes for character creation
        window.rolledAttributes = attributes;
        this.checkCharacterFormCompletion();
    }

    // Add visual feedback for form completion
    updateFormValidation() {
        const createBtn = document.getElementById('create-btn');
        const name = document.getElementById('character-name')?.value;
        const gender = document.querySelector('input[name="gender"]:checked')?.value;
        const race = document.getElementById('race-select')?.value;
        const characterClass = document.getElementById('class-select')?.value;
        const background = document.getElementById('background-select')?.value;
        const statMethod = document.querySelector('input[name="stat-method"]:checked')?.value;
        
        // Check what's missing
        const missing = [];
        if (!name) missing.push('Character Name');
        if (!gender) missing.push('Gender');
        if (!race) missing.push('Race');
        if (!characterClass) missing.push('Class');
        if (!background) missing.push('Background');
        if (statMethod !== 'pointbuy' && !window.rolledAttributes) missing.push('Roll Attributes');
        
        if (createBtn) {
            const isComplete = missing.length === 0;
            createBtn.disabled = !isComplete;
            
            if (missing.length > 0) {
                createBtn.textContent = `Complete: ${missing.join(', ')}`;
                createBtn.style.opacity = '0.6';
            } else {
                createBtn.textContent = 'Create Character';
                createBtn.style.opacity = '1';
            }
        }
    }

    // Check if character creation form is complete
    checkCharacterFormCompletion() {
        this.updateFormValidation();
    }

    // Create character and start game
    createCharacter() {
        try {
            window.gameCharacter = Character.createFromForm();
            
            if (!window.gameCharacter.isValid()) {
                this.showError('Please complete all character creation fields.');
                return;
            }

            console.log('Character created:', window.gameCharacter.name);
            if (window.audioManager) {
                window.audioManager.playSFX('newGame');
            }
            
            this.startGame();
            
        } catch (error) {
            console.error('Error creating character:', error);
            this.showError('Failed to create character. Please try again.');
        }
    }

    // Start the main game
    startGame() {
        this.gameState = 'playing';
        this.switchScreen('game-screen');
        if (window.audioManager) {
            window.audioManager.playMusic('traveling');
        }
        
        // Update character display
        this.updateCharacterDisplay();
        
        // Initialize starting quests (for demo purposes)
        this.initializeStartingQuests();
        
        // Start at Millhaven
        this.moveToLocation('millhaven');
        
        // Ensure fullscreen for game experience
        if (window.enterFullscreenOnGameStart) {
            window.enterFullscreenOnGameStart();
        }
    }

    // Initialize starting quests for new characters
    initializeStartingQuests() {
        if (window.questManager && window.gameCharacter) {
            // Check if this is a new character (no existing quest data)
            if (!window.gameCharacter.questData || window.gameCharacter.questData.length === 0) {
                // Add a starting quest
                window.questManager.addQuest('goblin_threat');
                console.log('Starting quest added to new character');
            }
        }
    }

    // Move to a new location
    moveToLocation(locationName) {
        if (window.isPaused && window.isPaused() && this.gameState === 'playing') return;
        
        const locationData = window.dataManager.getLocation(locationName);
        if (!locationData) {
            console.error(`Location '${locationName}' not found`);
            return;
        }

        this.currentLocation = locationName;
        window.gameCharacter.location = locationName;
        
        // Update location display
        const locationTitle = document.getElementById('location-title');
        const locationDescription = document.getElementById('location-description');
        const gameOptions = document.getElementById('game-options');

        if (locationTitle) {
            locationTitle.innerHTML = `<h2>${locationData.name || locationName}</h2>`;
        }

        if (locationDescription) {
            locationDescription.innerHTML = `<p>${locationData.description || 'You are in ' + locationName}</p>`;
        }

        // Generate location options
        if (gameOptions) {
            this.generateLocationOptions(locationData);
        }

        // Update character location display
        this.updateCharacterDisplay();

        // Play location-specific music
        this.playLocationMusic(locationName);
    }

    // Play location-specific music
    playLocationMusic(locationName) {
        if (!window.audioManager || !window.audioManager.isInitialized) {
            return;
        }

        // Map locations to music tracks
        const locationMusic = {
            'millhaven': 'traveling',
            'forest_path': 'traveling', 
            'goblin_camp': 'battle',
            'bandit_lair': 'battle',
            'capital_city': 'traveling',
            'mountain_pass': 'traveling',
            'dragons_lair': 'battle'
        };

        const musicTrack = locationMusic[locationName] || 'traveling';
        window.audioManager.playMusic(musicTrack);
    }

    // Generate interactive options for current location
    generateLocationOptions(locationData) {
        const gameOptions = document.getElementById('game-options');
        if (!gameOptions) return;

        let optionsHTML = '';

        // Add location-specific actions in a grid
        if (locationData.actions && locationData.actions.length > 0) {
            optionsHTML += '<h3>Available Actions:</h3>';
            optionsHTML += '<div class="actions-grid">';
            locationData.actions.forEach(action => {
                optionsHTML += `
                    <button class="option-btn" onclick="gameEngine.handleLocationAction('${action.id}')">
                        ${action.text}
                    </button>
                `;
            });
            optionsHTML += '</div>';
        }

        // Add general exploration option
        optionsHTML += '<div class="actions-grid" style="margin-top: 1rem;">';
        optionsHTML += `
            <button class="option-btn" onclick="gameEngine.exploreLocation()">
                Explore & Hunt
            </button>
        `;

        // Add NPCs to the same grid
        if (locationData.npcs) {
            locationData.npcs.forEach(npcName => {
                optionsHTML += `
                    <button class="option-btn" onclick="gameEngine.interactWithNPC('${npcName}')">
                        Talk to ${npcName}
                    </button>
                `;
            });
        }

        // Add shops to the same grid
        if (locationData.shops) {
            locationData.shops.forEach(shopName => {
                optionsHTML += `
                    <button class="option-btn" onclick="gameEngine.enterShop('${shopName}')">
                        Enter ${shopName}
                    </button>
                `;
            });
        }

        // Add rest option
        optionsHTML += `
            <button class="option-btn" onclick="gameEngine.restAtLocation()">
                Rest and Recover
            </button>
        `;
        optionsHTML += '</div>';

        // Add connections to other locations in a travel grid
        if (locationData.connections && locationData.connections.length > 0) {
            optionsHTML += '<hr style="margin: 1.5rem 0; border-color: #8b4513;">';
            optionsHTML += '<h4 style="color: #d4af37; margin: 0.5rem 0 1rem 0;">Travel Destinations:</h4>';
            optionsHTML += '<div class="travel-grid">';
            locationData.connections.forEach(connection => {
                optionsHTML += `
                    <button class="option-btn" onclick="gameEngine.moveToLocation('${connection}')">
                        Go to ${connection}
                    </button>
                `;
            });
            optionsHTML += '</div>';
        }

        gameOptions.innerHTML = optionsHTML;
    }

    // Explore current location for encounters
    exploreLocation() {
        if (window.isPaused && window.isPaused()) return;
        
        console.log('Exploring location for encounters...');
        if (window.audioManager) {
            window.audioManager.playSFX('click');
        }
        
        const locationData = window.dataManager.getLocation(this.currentLocation);
        if (!locationData || !locationData.enemies) {
            this.showMessage('You explore the area but find nothing of interest.');
            return;
        }

        // 60% chance of encounter
        const encounterChance = Math.random();
        if (encounterChance < 0.6) {
            const enemies = locationData.enemies;
            const randomEnemy = enemies[Math.floor(Math.random() * enemies.length)];
            this.triggerRandomEncounter(randomEnemy);
        } else {
            // No encounter, but maybe find some gold
            const goldFound = Math.floor(Math.random() * 15) + 5;
            window.gameCharacter.addGold(goldFound);
            this.updateCharacterDisplay();
            this.showMessage(`You explore the area and find ${goldFound} gold pieces hidden away.`);
        }
    }

    // Trigger random encounter
    triggerRandomEncounter(enemyName) {
        const enemyData = window.dataManager.getEnemy(enemyName);
        if (!enemyData) return;

        const encounterHTML = `
            <div class="encounter-dialog">
                <h3>Random Encounter!</h3>
                <p>A wild <strong>${enemyData.name}</strong> appears!</p>
                <p><em>${enemyData.description || 'It looks ready for a fight!'}</em></p>
                <div class="encounter-actions">
                    <button onclick="gameEngine.closeModal(); gameEngine.startCombat('${enemyName}')">
                        Fight!
                    </button>
                    <button onclick="gameEngine.closeModal(); gameEngine.attemptAvoidEncounter('${enemyName}')">
                        Try to Avoid
                    </button>
                </div>
            </div>
        `;

        this.showModal('Random Encounter', encounterHTML);
    }

    // Attempt to avoid encounter
    attemptAvoidEncounter(enemyName) {
        const avoidRoll = this.rollDice(20) + window.gameCharacter.getAttributeModifier('dexterity');
        
        if (avoidRoll >= 12) {
            this.showMessage('You successfully avoid the encounter and slip away quietly.');
        } else {
            this.showMessage('You failed to avoid the encounter! Combat begins!');
            setTimeout(() => {
                this.startCombat(enemyName);
            }, 2000);
        }
    }

    // Handle location-specific actions
    handleLocationAction(actionId) {
        if (window.isPaused && window.isPaused()) return;
        
        console.log(`Handling action: ${actionId}`);
        if (window.audioManager) {
            window.audioManager.playSFX('click');
        }
        
        // This can be expanded based on specific actions
        switch (actionId) {
            case 'rest':
                this.restAtLocation();
                break;
            case 'search':
                this.searchLocation();
                break;
            default:
                this.showMessage(`You ${actionId}.`);
        }
    }

    // Interact with an NPC
    interactWithNPC(npcName) {
        console.log(`Interacting with NPC: ${npcName}`);
        if (window.audioManager) {
            window.audioManager.playSFX('click');
        }
        
        // Convert display name to ID for dialogue system
        const npcId = window.dataManager.getNPCIdFromName(npcName);
        const npcData = window.dataManager.getNPC(npcId);
        if (npcData) {
            // Try to get dialogue data from the new dialogue system
            const dialogueInfo = window.dataManager.getNPCDialogueInfo(npcId);
            
            if (dialogueInfo && dialogueInfo.hasDialogues) {
                this.startDialogue(npcId);
            } else {
                // Fallback to simple dialogue from NPC data
                const fallbackText = npcData.dialogue || dialogueInfo?.greeting || `${npcData.name || npcName} greets you.`;
                this.showModal(`Talking to ${npcData.name || npcName}`, fallbackText);
            }
        } else {
            this.showMessage(`You approach ${npcName}.`);
        }
    }
    
    // Start interactive dialogue with an NPC
    startDialogue(npcName, dialogueKey = 'default') {
        const dialogueData = window.dataManager.getDialogue(npcName, dialogueKey);
        if (!dialogueData) {
            this.showMessage(`${npcName} doesn't seem to want to talk right now.`);
            return;
        }
        
        this.currentDialogue = {
            npcName: npcName,
            currentKey: dialogueKey,
            data: dialogueData
        };
        
        this.showDialogueModal(dialogueData);
    }
    
    // Show dialogue modal with interactive responses
    showDialogueModal(dialogueData) {
        const dialogue = dialogueData.dialogue;
        
        let dialogueHTML = `
            <div class="dialogue-container">
                <div class="npc-info" style="background: rgba(139, 69, 19, 0.3); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h4 style="color: #d4af37; margin: 0 0 0.5rem 0;">${dialogueData.npcName}</h4>
                    <p style="color: #e8d5b7; margin: 0; font-style: italic;">"${dialogueData.greeting}"</p>
                </div>
                
                <div class="dialogue-text" style="background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <p style="color: #e8d5b7; margin: 0; font-size: 1rem; line-height: 1.5;">${dialogue.text}</p>
                </div>
        `;
        
        if (dialogue.responses && dialogue.responses.length > 0) {
            dialogueHTML += `
                <div class="dialogue-responses" style="display: flex; flex-direction: column; gap: 0.5rem;">
                    <h5 style="color: #d4af37; margin: 0 0 0.5rem 0;">Choose your response:</h5>
            `;
            
            dialogue.responses.forEach((response, index) => {
                // Check if response requirements are met
                const canChoose = this.checkDialogueRequirements(response.requirements || []);
                const buttonStyle = canChoose 
                    ? 'background: linear-gradient(45deg, #8b4513, #a0522d); color: #e8d5b7; cursor: pointer;'
                    : 'background: linear-gradient(45deg, #666, #888); color: #999; cursor: not-allowed;';
                
                dialogueHTML += `
                    <button onclick="gameEngine.chooseDialogueResponse('${response.next}', '${response.action || ''}', ${index})" 
                            style="${buttonStyle} border: 1px solid #d4af37; padding: 0.75rem; border-radius: 4px; font-family: 'Cinzel', serif; font-size: 0.9rem;"
                            ${!canChoose ? 'disabled' : ''}>
                        ${response.text}
                    </button>
                `;
            });
            
            dialogueHTML += '</div>';
        } else {
            // End of conversation
            dialogueHTML += `
                <div style="text-align: center; margin-top: 1rem;">
                    <button onclick="gameEngine.closeModal()" 
                            style="background: linear-gradient(45deg, #8b4513, #a0522d); color: #e8d5b7; border: 1px solid #d4af37; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-family: 'Cinzel', serif;">
                        End Conversation
                    </button>
                </div>
            `;
        }
        
        dialogueHTML += '</div>';
        
        this.showModal(`Conversation with ${dialogueData.npcName}`, dialogueHTML, true);
    }
    
    // Choose a dialogue response
    chooseDialogueResponse(nextKey, action, responseIndex) {
        if (action) {
            this.executeDialogueAction(action);
        }
        
        if (nextKey === 'goodbye' || nextKey === 'end_conversation') {
            this.closeModal();
            return;
        }
        
        if (nextKey && this.currentDialogue) {
            this.startDialogue(this.currentDialogue.npcName, nextKey);
        } else {
            this.closeModal();
        }
    }
    
    // Execute dialogue actions
    executeDialogueAction(action) {
        if (!action) return;
        
        const [actionType, actionValue] = action.split(':');
        
        switch (actionType) {
            case 'start_quest':
                if (window.questManager) {
                    window.questManager.addQuest(actionValue);
                    this.showMessage(`Quest started: ${actionValue}`, 3000);
                }
                break;
            case 'open_shop':
                setTimeout(() => {
                    this.closeModal();
                    // Map NPC ID to shop name
                    const shopMapping = {
                        'clement_bugbee': "Bugbee's Blades & Brews",
                        'tianna': "The Thirsty Hare",
                        'kiki': "Kiki's Potions"
                    };
                    const shopName = shopMapping[this.currentDialogue.npcName] || actionValue;
                    this.enterShop(shopName);
                }, 500);
                break;
            case 'buy_meal':
                if (window.gameCharacter && window.gameCharacter.spendGold(5)) {
                    window.gameCharacter.heal(10);
                    this.updateCharacterDisplay();
                    this.showMessage('You enjoy a hearty meal and feel refreshed!', 3000);
                } else {
                    this.showMessage('You don\'t have enough gold for a meal.', 3000);
                }
                break;
            case 'rest_at_inn':
                if (window.gameCharacter && window.gameCharacter.spendGold(10)) {
                    window.gameCharacter.heal();
                    this.advanceDay();
                    this.updateCharacterDisplay();
                    this.showMessage('You rest comfortably at the inn and wake refreshed for a new day!', 4000);
                } else {
                    this.showMessage('You don\'t have enough gold for a room.', 3000);
                }
                break;
            case 'heal_player':
                if (window.gameCharacter) {
                    window.gameCharacter.heal(15);
                    this.updateCharacterDisplay();
                }
                break;
            case 'advance_day':
                this.advanceDay();
                this.updateCharacterDisplay();
                break;
            case 'end_conversation':
                this.closeModal();
                break;
            default:
                console.log(`Unknown dialogue action: ${action}`);
        }
    }
    
    // Check if dialogue requirements are met
    checkDialogueRequirements(requirements) {
        if (!requirements || requirements.length === 0) return true;
        
        for (const requirement of requirements) {
            const [reqType, reqValue] = requirement.split(':');
            
            switch (reqType) {
                case 'gold':
                    if (!window.gameCharacter || window.gameCharacter.gold < parseInt(reqValue)) {
                        return false;
                    }
                    break;
                case 'level':
                    if (!window.gameCharacter || window.gameCharacter.level < parseInt(reqValue)) {
                        return false;
                    }
                    break;
                case 'quest_active':
                    if (!window.questManager) {
                        return false;
                    }
                    // Check if quest manager has the quest active
                    if (window.questManager.playerQuests && !window.questManager.playerQuests.has(reqValue)) {
                        return false;
                    }
                    break;
                case 'quest_completed':
                    if (!window.questManager) {
                        return false;
                    }
                    // Check if quest is completed
                    const quest = window.questManager.playerQuests ? window.questManager.playerQuests.get(reqValue) : null;
                    if (!quest || quest.status !== 'completed') {
                        return false;
                    }
                    break;
                // Add more requirement types as needed
            }
        }
        
        return true;
    }

    // Enter a shop
    enterShop(shopName) {
        console.log(`Entering shop: ${shopName}`);
        if (window.audioManager) {
            window.audioManager.playSFX('click');
        }
        
        const shopData = window.dataManager.getShop(shopName);
        if (shopData) {
            // Play shop music and voice line
            if (window.audioManager) {
                window.audioManager.playMusic('blacksmith');
                if (shopData.keeper) {
                    window.audioManager.playVoiceLine(shopData.keeper, 'greeting');
                }
            }
            
            this.showShopInterface(shopName, shopData);
        } else {
            this.showMessage(`The ${shopName} appears to be closed.`);
        }
    }

    // Show shop interface
    showShopInterface(shopName, shopData) {
        let shopHTML = `
            <div class="shop-interface">
                <div class="shop-header">
                    <h3 style="color: #d4af37; margin: 0 0 0.5rem 0;">${shopName}</h3>
                    <div class="merchant-info">
                        <p style="color: #90ee90; margin: 0.25rem 0;"><strong>${shopData.merchant_name}</strong> (${shopData.type})</p>
                        <p style="color: #e8d5b7; font-style: italic; margin: 0.5rem 0;">"${shopData.merchant_greeting}"</p>
                        <p style="color: #999; font-size: 0.9rem; margin: 0.5rem 0;">${shopData.description.replace(/\\n/g, '<br>')}</p>
                    </div>
                </div>
                
                <div class="player-gold" style="background: rgba(212, 175, 55, 0.2); padding: 0.75rem; border-radius: 6px; margin: 1rem 0; text-align: center;">
                    <p style="color: #d4af37; margin: 0; font-size: 1.1rem;"><strong>Your Gold: ${window.gameCharacter ? window.gameCharacter.gold : 0}</strong></p>
                </div>

                <div class="shop-inventory">
                    <h4 style="color: #87ceeb; margin: 1rem 0 0.5rem 0;">Shop Inventory</h4>
        `;

        if (shopData.inventory && Object.keys(shopData.inventory).length > 0) {
            let itemNumber = 1;
            for (const [itemName, itemInfo] of Object.entries(shopData.inventory)) {
                const itemData = window.dataManager.getItem(itemName);
                
                // Calculate price (with discount if on sale)
                let basePrice = itemData?.cost || itemInfo.price || 10;
                let finalPrice = basePrice;
                let saleInfo = '';
                
                if (itemInfo.on_sale && itemInfo.discount && itemInfo.discount > 0) {
                    const discountAmount = Math.floor(basePrice * (itemInfo.discount / 100));
                    finalPrice = Math.max(1, basePrice - discountAmount); // Ensure price never goes below 1
                    saleInfo = `<span style="color: #ff6b6b; font-weight: bold;">ON SALE ${itemInfo.discount}% OFF!</span> <span style="text-decoration: line-through; color: #999;">${basePrice}g</span>`;
                }

                const quantity = itemInfo.quantity || 0;
                const inStock = quantity > 0;
                const canAfford = window.gameCharacter ? window.gameCharacter.gold >= finalPrice : false;
                const canBuy = inStock && canAfford;

                shopHTML += `
                    <div class="shop-item" style="
                        display: flex; 
                        justify-content: space-between; 
                        align-items: center; 
                        padding: 0.75rem; 
                        margin: 0.5rem 0; 
                        background: rgba(139, 69, 19, 0.2); 
                        border-radius: 6px; 
                        border-left: 4px solid ${inStock ? '#228b22' : '#8b0000'};
                        ${!inStock ? 'opacity: 0.6;' : ''}
                    ">
                        <div class="item-details" style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                                <span style="color: #d4af37; font-weight: bold;">${itemNumber}.</span>
                                <strong style="color: #e8d5b7;">${itemName}</strong>
                                ${this.getItemRarityBadge(itemData)}
                            </div>
                            
                            <p style="color: #ccc; margin: 0.25rem 0; font-size: 0.9rem;">
                                ${itemData?.description || 'A fine item for sale.'}
                            </p>
                            
                            <div style="display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem;">
                                <div class="price-info">
                                    ${saleInfo ? saleInfo + ` <span style="color: #90ee90; font-weight: bold;">${finalPrice}g</span>` : 
                                      `<span style="color: #90ee90; font-weight: bold;">${finalPrice}g</span>`}
                                </div>
                                <div style="color: ${inStock ? '#90ee90' : '#ff6b6b'};">
                                    Stock: ${quantity}
                                </div>
                            </div>
                        </div>
                        
                        <div class="item-actions">
                            <button onclick="gameEngine.buyShopItem('${shopName}', '${itemName}', ${finalPrice})" 
                                    style="
                                        background: ${canBuy ? 'linear-gradient(45deg, #228b22, #32cd32)' : 'linear-gradient(45deg, #666, #888)'};
                                        color: white;
                                        border: none;
                                        padding: 0.5rem 1rem;
                                        border-radius: 4px;
                                        cursor: ${canBuy ? 'pointer' : 'not-allowed'};
                                        font-family: 'Cinzel', serif;
                                    "
                                    ${!canBuy ? 'disabled' : ''}>
                                ${!inStock ? 'Out of Stock' : (!canAfford ? 'Too Expensive' : 'Buy')}
                            </button>
                        </div>
                    </div>
                `;
                itemNumber++;
            }
        } else {
            shopHTML += '<p style="color: #999; font-style: italic; text-align: center; padding: 2rem;">This shop has no items available.</p>';
        }

        shopHTML += `
                </div>
                
                <div class="shop-actions" style="margin-top: 1.5rem; text-align: center;">
                    <button onclick="gameEngine.leaveShop('${shopName}', '${shopData.merchant_goodbye}')" 
                            style="
                                background: linear-gradient(45deg, #8b4513, #a0522d);
                                color: #e8d5b7;
                                border: 2px solid #d4af37;
                                padding: 0.75rem 1.5rem;
                                border-radius: 6px;
                                cursor: pointer;
                                font-family: 'Cinzel', serif;
                                font-size: 1rem;
                            ">
                        Leave Shop
                    </button>
                </div>
            </div>
        `;

        this.showModal(shopName, shopHTML, true);
    }

    // Get item rarity badge for display
    getItemRarityBadge(itemData) {
        if (!itemData || !itemData.rarity) return '';
        
        const rarityColors = {
            'common': '#ffffff',
            'uncommon': '#90ee90', 
            'rare': '#87ceeb',
            'epic': '#dda0dd',
            'legendary': '#ffd700'
        };
        
        const color = rarityColors[itemData.rarity.toLowerCase()] || '#ffffff';
        return `<span style="
            background: ${color}; 
            color: #000; 
            padding: 0.15rem 0.4rem; 
            border-radius: 3px; 
            font-size: 0.7rem; 
            font-weight: bold;
            text-transform: uppercase;
        ">${itemData.rarity}</span>`;
    }

    // Get rarity color for items
    getRarityColor(rarity) {
        const rarityColors = {
            'common': '#ffffff',
            'uncommon': '#90ee90', 
            'rare': '#87ceeb',
            'epic': '#dda0dd',
            'legendary': '#ffd700'
        };
        return rarityColors[rarity?.toLowerCase()] || '#ffffff';
    }

    // Buy an item from shop
    buyShopItem(shopName, itemName, price) {
        if (!window.gameCharacter) {
            this.showMessage('No character found!', 3000);
            return;
        }

        const shopData = window.dataManager.getShop(shopName);
        if (!shopData || !shopData.inventory[itemName]) {
            this.showMessage('Item not found in shop!', 3000);
            return;
        }

        const itemInfo = shopData.inventory[itemName];
        
        // Check stock
        if (itemInfo.quantity <= 0) {
            this.showMessage('This item is out of stock!', 3000);
            return;
        }

        // Check if player can afford it
        if (!window.gameCharacter.canAfford(price)) {
            this.showMessage(`You need ${price - window.gameCharacter.gold} more gold!`, 3000);
            return;
        }

        // Make the purchase
        if (window.gameCharacter.spendGold(price)) {
            // Add item to inventory
            window.gameCharacter.addItem(itemName);
            
            // Reduce shop stock
            itemInfo.quantity--;
            
            // Play purchase sound
            if (window.audioManager && shopData.merchant_id) {
                window.audioManager.playVoiceLine(shopData.merchant_id, 'purchase');
            }
            
            // Update character display
            this.updateCharacterDisplay();
            
            // Show success message and refresh shop
            this.showMessage(`Purchased ${itemName} for ${price} gold!`, 3000);
            
            // Refresh the shop interface to show updated stock and gold
            setTimeout(() => {
                this.showShopInterface(shopName, shopData);
            }, 1000);
        } else {
            this.showMessage('Transaction failed!', 3000);
        }
    }

    // Leave shop
    leaveShop(shopName, goodbyeMessage) {
        const shopData = window.dataManager.getShop(shopName);
        
        // Play goodbye message
        if (goodbyeMessage) {
            this.showMessage(`"${goodbyeMessage}" - Thank you for visiting!`, 2000);
        }
        
        // Play goodbye sound
        if (window.audioManager && shopData && shopData.merchant_id) {
            window.audioManager.playVoiceLine(shopData.merchant_id, 'goodbye');
        }
        
        // Close modal
        this.closeModal();
        
        // Return to normal music
        if (window.audioManager) {
            window.audioManager.playMusic('traveling');
        }
    }

    // Get current shop data (helper method)
    getCurrentShopData() {
        const modalTitle = document.getElementById('modal-title');
        if (modalTitle) {
            return window.dataManager.getShop(modalTitle.textContent);
        }
        return null;
    }

    // Get current shop name (helper method)
    getCurrentShopName() {
        const modalTitle = document.getElementById('modal-title');
        return modalTitle ? modalTitle.textContent : null;
    }

    // Get current game day
    getCurrentDay() {
        return this.gameDay;
    }

    // Advance to the next day (clears shop sales cache)
    advanceDay() {
        this.gameDay++;
        this.dayStartTime = Date.now();
        
        // Clear shop sales cache so new sales are generated
        this.shopSalesCache = {};
        
        // Update UI
        this.updateCharacterDisplay();
        
        // Show day change message
        this.showMessage(`A new day dawns... Day ${this.gameDay}`, 3000);
        
        console.log(`Advanced to day ${this.gameDay}`);
    }

    // Check if a new day should start (for future time-based progression)
    checkDayProgression() {
        // This could be expanded to automatically advance days based on real time
        // or specific in-game actions like resting at an inn
        const hoursPerDay = 24; // Real hours per game day (could be much shorter)
        const msPerDay = hoursPerDay * 60 * 60 * 1000;
        
        if (Date.now() - this.dayStartTime >= msPerDay) {
            this.advanceDay();
        }
    }

    // Rest at location (advances day)
    restAtLocation() {
        if (!window.gameCharacter) {
            this.showMessage('No character found!', 3000);
            return;
        }

        // Heal character when resting
        window.gameCharacter.heal();
        
        // Advance to next day
        this.advanceDay();
        
        // Update display
        this.updateCharacterDisplay();
        
        this.showMessage('You rest through the night and wake refreshed. Your health has been restored!', 4000);
    }

    // Update character display in the UI
    updateCharacterDisplay() {
        if (!window.gameCharacter) return;
        
        // Update character panel information
        const nameDisplay = document.getElementById('character-name-display');
        const levelDisplay = document.getElementById('char-level');
        const healthDisplay = document.getElementById('char-health');
        const maxHealthDisplay = document.getElementById('char-max-health');
        const goldDisplay = document.getElementById('char-gold');
        const locationDisplay = document.getElementById('char-location');
        
        if (nameDisplay) {
            nameDisplay.textContent = window.gameCharacter.name;
        }
        
        if (levelDisplay) {
            levelDisplay.textContent = window.gameCharacter.level || 1;
        }
        
        if (healthDisplay) {
            healthDisplay.textContent = window.gameCharacter.health || window.gameCharacter.maxHealth;
        }
        
        if (maxHealthDisplay) {
            maxHealthDisplay.textContent = window.gameCharacter.maxHealth || 10;
        }
        
        if (goldDisplay) {
            goldDisplay.textContent = window.gameCharacter.gold || 0;
        }
        
        if (locationDisplay) {
            locationDisplay.textContent = window.gameCharacter.location || 'Unknown';
        }
        
        // Update day counter in a visible location (add it to character panel)
        const charPanel = document.querySelector('.character-stats');
        if (charPanel) {
            // Remove existing day display if present
            const existingDayDisplay = charPanel.querySelector('.day-counter');
            if (existingDayDisplay) {
                existingDayDisplay.remove();
            }
            
            // Add new day display at the top
            const dayDisplay = document.createElement('p');
            dayDisplay.className = 'day-counter';
            dayDisplay.innerHTML = `<strong>Day:</strong> <span style="color: #d4af37;">${this.gameDay}</span>`;
            charPanel.insertBefore(dayDisplay, charPanel.firstChild);
        }
        
        console.log(`Character display updated - Day ${this.gameDay}`);
    }

    // Save game state including day counter
    saveGame() {
        try {
            if (!window.gameCharacter) {
                this.showMessage('No character to save!');
                return;
            }

            const saveData = {
                character: window.gameCharacter.toSaveObject(),
                gameDay: this.gameDay,
                dayStartTime: this.dayStartTime,
                shopSalesCache: this.shopSalesCache,
                currentLocation: this.currentLocation,
                gameState: this.gameState,
                journal: this.journal,
                timestamp: Date.now()
            };

            localStorage.setItem(this.saveKey, JSON.stringify(saveData));
            this.showMessage('Game saved successfully!', 'success');
            console.log(`Game saved - Day ${this.gameDay}`);

        } catch (error) {
            console.error('Error saving game:', error);
            this.showMessage('Failed to save game!');
        }
    }

    // Load game state including day counter
    loadGame() {
        try {
            const savedData = localStorage.getItem(this.saveKey);
            if (!savedData) {
                this.showMessage('No saved game found!');
                return false;
            }

            const saveData = JSON.parse(savedData);
            
            // Restore day counter and shop cache
            this.gameDay = saveData.gameDay || 1;
            this.dayStartTime = saveData.dayStartTime || Date.now();
            this.shopSalesCache = saveData.shopSalesCache || {};
            
            // Handle legacy location names
            let location = saveData.currentLocation || 'millhaven';
            if (location === 'Village' || location === 'Millhaven') {
                location = 'millhaven'; // Convert old save files
            }
            this.currentLocation = location;
            
            this.gameState = saveData.gameState || 'playing';
            this.journal = saveData.journal || { rumors: [], quests: [] };

            // Restore character with better error handling
            console.log('Save data check:', {
                hasCharacter: !!saveData.character,
                hasCharacterClass: !!window.Character,
                characterData: saveData.character
            });
            
            if (!saveData.character) {
                throw new Error('No character data found in save file');
            }
            
            if (!window.Character) {
                throw new Error('Character class not available - character.js may not be loaded');
            }
            
            try {
                window.gameCharacter = Character.fromSaveObject(saveData.character);
                
                // Start the game with loaded state
                this.switchScreen('game-screen');
                this.moveToLocation(this.currentLocation);
                this.updateCharacterDisplay();
                
                if (window.audioManager) {
                    window.audioManager.playMusic('traveling');
                }
                
                this.showMessage('Game loaded successfully!', 'success');
                console.log(`Game loaded - Day ${this.gameDay}`);
                return true;
            } catch (characterError) {
                console.error('Error creating character from save data:', characterError);
                throw new Error(`Failed to restore character: ${characterError.message}`);
            }

        } catch (error) {
            console.error('Error loading game:', error);
            
            // Show detailed error and offer to clear save data
            const errorMessage = `
                <div style="text-align: left;">
                    <p><strong>Failed to load save file:</strong></p>
                    <p style="color: #ffcccc; font-family: monospace; font-size: 0.9rem; margin: 1rem 0; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 4px;">${error.message}</p>
                    <p>This usually happens when:</p>
                    <ul style="margin: 1rem 0; color: #ddd;">
                        <li>Save file is from an older version</li>
                        <li>Save file was corrupted</li>
                        <li>Game files were updated</li>
                    </ul>
                    <p><strong>Would you like to clear the save data and start fresh?</strong></p>
                </div>
                <div style="margin-top: 1.5rem; text-align: center;">
                    <button onclick="window.gameEngine.clearSaveDataAndRestart()" style="
                        background: #8b0000;
                        color: white;
                        border: 1px solid #ff6666;
                        padding: 10px 20px;
                        margin: 0 10px;
                        cursor: pointer;
                        border-radius: 4px;
                        font-family: 'Cinzel', serif;
                    ">Clear Save & Start New Game</button>
                    <button onclick="window.gameEngine.closeModal()" style="
                        background: #2d4a5a;
                        color: white;
                        border: 1px solid #4a7c8b;
                        padding: 10px 20px;
                        margin: 0 10px;
                        cursor: pointer;
                        border-radius: 4px;
                        font-family: 'Cinzel', serif;
                    ">Cancel</button>
                </div>
            `;
            
            this.showModal(errorMessage, 'Save File Error');
            return false;
        }
    }

    // Clear corrupted save data (for debugging)
    clearSaveData() {
        try {
            localStorage.removeItem(this.saveKey);
            this.showMessage('Save data cleared!', 'info');
            console.log('Save data cleared');
        } catch (error) {
            console.error('Error clearing save data:', error);
            this.showMessage('Failed to clear save data!');
        }
    }

    // Clear save data and restart game
    clearSaveDataAndRestart() {
        try {
            localStorage.removeItem(this.saveKey);
            this.showMessage('Save data cleared! Starting new game...', 'success');
            console.log('Save data cleared and restarting');
            
            // Close modal and start new game
            this.closeModal();
            
            // Small delay to let the user see the message
            setTimeout(() => {
                this.startNewGame();
            }, 1000);
            
        } catch (error) {
            console.error('Error clearing save data:', error);
            this.showMessage('Failed to clear save data!');
        }
    }

    // Show success/info message
    showMessage(message, type = 'info') {
        // Handle legacy calls where second parameter is a timeout number
        if (typeof type === 'number') {
            type = 'info';
        }
        
        const messageDiv = document.createElement('div');
        const bgColor = type === 'success' ? '#2d5a27' : type === 'warning' ? '#8b6914' : '#2d4a5a';
        const borderColor = type === 'success' ? '#4a7c59' : type === 'warning' ? '#d4af37' : '#4a7c8b';
        
        messageDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(45deg, ${bgColor}, ${bgColor}dd);
            color: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid ${borderColor};
            z-index: 10000;
            text-align: center;
            font-family: 'Cinzel', serif;
            max-width: 400px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
        `;
        
        messageDiv.innerHTML = `
            <h3 style="margin: 0 0 10px 0; color: #ffffff;">${type.charAt(0).toUpperCase() + type.slice(1)}</h3>
            <p style="margin: 0 0 15px 0;">${message}</p>
            <button onclick="this.parentElement.remove()" style="
                background: ${bgColor};
                color: white;
                border: 1px solid ${borderColor};
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
                font-family: 'Cinzel', serif;
            ">OK</button>
        `;
        
        document.body.appendChild(messageDiv);
        
        // Auto-remove after 3 seconds for info messages
        if (type === 'info') {
            setTimeout(() => {
                if (messageDiv.parentElement) {
                    messageDiv.remove();
                }
            }, 3000);
        }
    }

    // Show modal dialog
    showModal(content, title = '', isLarge = false) {
        const modalOverlay = document.getElementById('modal-overlay');
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');

        if (modalTitle) modalTitle.textContent = title;
        if (modalContent) modalContent.innerHTML = content;
        
        if (modalOverlay && modal) {
            modalOverlay.classList.add('active');
            modal.classList.add('active');
            this.activeModal = modal;
        }
    }

    // Close modal dialog
    closeModal() {
        const modalOverlay = document.getElementById('modal-overlay');
        const modal = document.getElementById('modal');
        
        if (modalOverlay && modal) {
            modalOverlay.classList.remove('active');
            modal.classList.remove('active');
            this.activeModal = null;
        }
    }

    // Show journal/quest log
    showJournal() {
        if (!this.journal) {
            this.showMessage('Journal not available!');
            return;
        }

        let journalContent = '<div class="journal-content">';
        
        // Active Quests
        journalContent += '<h3>Active Quests</h3>';
        if (this.journal.quests && this.journal.quests.length > 0) {
            journalContent += '<ul>';
            this.journal.quests.forEach(quest => {
                journalContent += `<li><strong>${quest.name}</strong>: ${quest.description}</li>`;
            });
            journalContent += '</ul>';
        } else {
            journalContent += '<p>No active quests.</p>';
        }

        // Rumors
        journalContent += '<h3>Rumors</h3>';
        if (this.journal.rumors && this.journal.rumors.length > 0) {
            journalContent += '<ul>';
            this.journal.rumors.forEach(rumor => {
                journalContent += `<li>${rumor.text}</li>`;
            });
            journalContent += '</ul>';
        } else {
            journalContent += '<p>No rumors heard.</p>';
        }

        journalContent += '</div>';
        
        this.showModal(journalContent, 'Journal');
    }

    // Show error message
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(45deg, #8b0000, #a00000);
            color: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #ff0000;
            z-index: 10000;
            text-align: center;
            font-family: 'Cinzel', serif;
            max-width: 400px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
        `;
        errorDiv.innerHTML = `
            <h3 style="margin: 0 0 10px 0; color: #ffcccc;">Error</h3>
            <p style="margin: 0 0 15px 0;">${message}</p>
            <button onclick="this.parentElement.remove()" style="
                background: #660000;
                color: white;
                border: 1px solid #ff0000;
                padding: 8px 16px;
                cursor: pointer;
                border-radius: 4px;
                font-family: 'Cinzel', serif;
            ">OK</button>
        `;
        document.body.appendChild(errorDiv);
    }
}

// Create global game engine instance
window.gameEngine = new GameEngine();

// Initialize developer tools
window.developerTools = new DeveloperTools();

// Global functions for HTML onclick handlers
function startNewGame() {
    window.gameEngine.startNewGame();
}

function loadGame() {
    window.gameEngine.loadGame();
}

function showChangelog() {
    window.gameEngine.showChangelog();
}

function showSettings() {
    window.gameEngine.showSettings();
}

function exitGame() {
    window.gameEngine.exitGame();
}

function createCharacter() {
    window.gameEngine.createCharacter();
}

function showTitleScreen() {
    window.gameEngine.showTitleScreen();
}

function closeModal() {
    window.gameEngine.closeModal();
}

function showInventory() {
    if (window.gameEngine && window.gameEngine.showModal) {
        window.gameEngine.showModal('Inventory is empty', 'Inventory');
    }
}

function showJournal() {
    if (window.gameEngine && window.gameEngine.showJournal) {
        window.gameEngine.showJournal();
    }
}

function saveGame() {
    if (window.gameEngine && window.gameEngine.saveGame) {
        window.gameEngine.saveGame();
    }
}
