// Developer tools and console system

class DeveloperTools {
    constructor() {
        this.isEnabled = false;
        this.isMenuOpen = false;
        this.consoleHistory = [];
        this.consoleHistoryIndex = -1;
        this.commands = {};
        this.presetData = null; // Store loaded preset data
        
        this.setupCommands();
        this.setupKeyListener();
        this.loadPresetData(); // Load presets on initialization
    }

    // Initialize developer mode
    enable() {
        this.isEnabled = true;
        console.log('Developer mode enabled. Press ` to open developer menu.');
        
        // Add developer objects to window for console access
        window.dev = {
            tools: this,
            game: window.gameEngine,
            character: () => window.gameCharacter,
            data: window.dataManager,
            audio: window.audioManager,
            quest: window.questManager,
            addGold: (amount) => this.cheatAddGold(amount),
            setLevel: (level) => this.cheatSetLevel(level),
            heal: () => this.cheatHeal(),
            godMode: () => this.cheatGodMode(),
            showData: (type) => this.showDataViewer(type),
            help: () => this.showDevHelp(),
            // Quest shortcuts
            addQuest: (questId) => window.gameEngine.addQuest(questId),
            completeQuest: (questId) => window.gameEngine.completeQuest(questId),
            listQuests: () => window.questManager?.getAllPlayerQuests() || [],
            testQuests: () => {
                const questIds = ['goblin_threat', 'lost_treasure', 'missing_child', 'cursed_artifact'];
                questIds.forEach(id => window.gameEngine.addQuest(id));
                console.log('Test quests added! Check your journal.');
            },
            // Preset character shortcuts
            loadPreset: (type) => this.loadPresetCharacter(type),
            warrior: () => this.loadPresetCharacter('warrior'),
            rogue: () => this.loadPresetCharacter('rogue'),
            wizard: () => this.loadPresetCharacter('wizard'),
            cleric: () => this.loadPresetCharacter('cleric'),
            ranger: () => this.loadPresetCharacter('ranger'),
            barbarian: () => this.loadPresetCharacter('barbarian'),
            maxed: () => this.loadPresetCharacter('maxed'),
            merchant: () => this.loadPresetCharacter('merchant')
        };
    }

    // Setup keyboard listener
    setupKeyListener() {
        document.addEventListener('keydown', (e) => {
            if (!this.isEnabled) return;
            
            // Toggle developer menu with backtick key
            if (e.key === '`' || e.key === '~') {
                e.preventDefault();
                this.toggleMenu();
            }
            
            // Close menu with Escape
            if (e.key === 'Escape' && this.isMenuOpen) {
                this.closeMenu();
            }
        });
    }

    // Setup developer commands
    setupCommands() {
        this.commands = {
            help: {
                description: 'Show available commands',
                execute: () => this.showHelp()
            },
            clear: {
                description: 'Clear console output',
                execute: () => this.clearConsole()
            },
            addgold: {
                description: 'Add gold to character (usage: addgold 100)',
                execute: (args) => this.cheatAddGold(parseInt(args[0]) || 100)
            },
            setlevel: {
                description: 'Set character level (usage: setlevel 5)',
                execute: (args) => this.cheatSetLevel(parseInt(args[0]) || 1)
            },
            heal: {
                description: 'Fully heal character',
                execute: () => this.cheatHeal()
            },
            godmode: {
                description: 'Toggle god mode (infinite health)',
                execute: () => this.cheatGodMode()
            },
            teleport: {
                description: 'Teleport to location (usage: teleport Village)',
                execute: (args) => this.cheatTeleport(args[0])
            },
            showdata: {
                description: 'Show raw data (usage: showdata races)',
                execute: (args) => this.showDataViewer(args[0])
            },
            reload: {
                description: 'Reload game data',
                execute: () => this.reloadGameData()
            },
            save: {
                description: 'Force save game',
                execute: () => window.gameEngine.saveGame()
            },
            reset: {
                description: 'Reset to title screen',
                execute: () => this.resetGame()
            }
        };

        // Setup quest-specific commands
        this.setupQuestCommands();

        // Quest system developer commands
        this.setupQuestCommands();
    }

    // Setup quest commands
    setupQuestCommands() {
        // Add quest management commands
        this.commands.addquest = {
            name: 'addquest',
            description: 'Add a quest to player quest log',
            usage: 'addquest <questId>',
            execute: (args) => {
                if (!args[0]) {
                    return 'Usage: addquest <questId>\nAvailable quests: goblin_threat, lost_treasure, missing_child, cursed_artifact';
                }
                
                if (window.gameEngine.addQuest(args[0])) {
                    return `Quest "${args[0]}" added successfully!`;
                } else {
                    return `Failed to add quest "${args[0]}". Make sure the quest ID is valid.`;
                }
            }
        };

        this.commands.completequest = {
            name: 'completequest',
            description: 'Complete a quest (marks all objectives as done)',
            usage: 'completequest <questId>',
            execute: (args) => {
                if (!args[0]) {
                    return 'Usage: completequest <questId>';
                }
                
                const quest = window.questManager?.getQuest(args[0]);
                if (!quest) {
                    return `Quest "${args[0]}" not found in player's quest log.`;
                }
                
                // Complete all objectives
                quest.objectives.forEach(obj => {
                    window.questManager.updateObjective(args[0], obj.id);
                });
                
                return `All objectives completed for quest "${quest.name}". You can now complete the quest.`;
            }
        };

        this.commands.objective = {
            name: 'objective',
            description: 'Complete a specific quest objective',
            usage: 'objective <questId> <objectiveId>',
            execute: (args) => {
                if (!args[0] || !args[1]) {
                    return 'Usage: objective <questId> <objectiveId>';
                }
                
                if (window.gameEngine.updateQuestObjective(args[0], parseInt(args[1]))) {
                    return `Objective ${args[1]} completed for quest "${args[0]}"!`;
                } else {
                    return `Failed to complete objective. Check quest ID and objective ID.`;
                }
            }
        };

        this.commands.listquests = {
            name: 'listquests',
            description: 'List all player quests',
            usage: 'listquests [status]',
            execute: (args) => {
                if (!window.questManager) {
                    return 'Quest manager not initialized.';
                }
                
                const status = args[0] || 'all';
                let quests;
                
                if (status === 'all') {
                    quests = window.questManager.getAllPlayerQuests();
                } else {
                    quests = window.questManager.getQuestsByStatus(status);
                }
                
                if (quests.length === 0) {
                    return status === 'all' ? 'No quests found.' : `No ${status} quests found.`;
                }
                
                let result = status === 'all' ? 'All Player Quests:\n' : `${status.toUpperCase()} Quests:\n`;
                quests.forEach(quest => {
                    const progress = quest.playerProgress ? 
                        `${quest.playerProgress.objectivesCompleted}/${quest.objectives.length}` : '0/0';
                    result += `- ${quest.name} (${quest.status}) [${progress}]\n`;
                });
                
                return result;
            }
        };

        this.commands.questinfo = {
            name: 'questinfo',
            description: 'Show detailed information about a quest',
            usage: 'questinfo <questId>',
            execute: (args) => {
                if (!args[0]) {
                    return 'Usage: questinfo <questId>';
                }
                
                const quest = window.questManager?.getQuest(args[0]);
                if (!quest) {
                    return `Quest "${args[0]}" not found.`;
                }
                
                let info = `Quest: ${quest.name}\n`;
                info += `Status: ${quest.status}\n`;
                info += `Description: ${quest.description}\n`;
                info += `Progress: ${quest.playerProgress?.objectivesCompleted || 0}/${quest.objectives.length}\n`;
                info += `Objectives:\n`;
                
                quest.objectives.forEach(obj => {
                    const status = obj.status === 'complete' ? '✓' : '○';
                    info += `  ${status} ${obj.description}\n`;
                });
                
                return info;
            }
        };

        // Add quick test function
        this.commands.testquests = {
            name: 'testquests',
            description: 'Add all available quests for testing',
            usage: 'testquests',
            execute: () => {
                const questIds = ['goblin_threat', 'lost_treasure', 'missing_child', 'cursed_artifact'];
                let added = 0;
                
                questIds.forEach(questId => {
                    if (window.gameEngine.addQuest(questId)) {
                        added++;
                    }
                });
                
                return `Added ${added} test quests to your journal. Check your Quest Log!`;
            }
        };
    }

    // Toggle developer menu
    toggleMenu() {
        if (this.isMenuOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    // Open developer menu
    openMenu() {
        this.isMenuOpen = true;
        this.createMenuInterface();
    }

    // Close developer menu
    closeMenu() {
        this.isMenuOpen = false;
        const devMenu = document.getElementById('dev-menu');
        if (devMenu) {
            devMenu.remove();
        }
    }

    // Create menu interface
    createMenuInterface() {
        // Remove existing menu if present
        this.closeMenu();
        
        const menuHTML = `
            <div id="dev-menu" style="
                position: fixed;
                top: 10px;
                right: 10px;
                width: 600px;
                height: 500px;
                background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
                border: 2px solid #00ff00;
                border-radius: 8px;
                z-index: 10000;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            ">
                <div style="
                    background: #333;
                    padding: 8px;
                    border-bottom: 1px solid #00ff00;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="font-weight: bold;">🛠️ Developer Tools</span>
                    <button onclick="window.dev.tools.closeMenu()" style="
                        background: #ff0000;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        cursor: pointer;
                        border-radius: 3px;
                    ">✕</button>
                </div>
                
                <div style="display: flex; height: calc(100% - 40px);">
                    <div style="
                        width: 150px;
                        background: #2a2a2a;
                        border-right: 1px solid #00ff00;
                        padding: 10px;
                    ">
                        <div style="margin-bottom: 5px; font-weight: bold;">MENU</div>
                        <button onclick="window.dev.tools.showConsole()" class="dev-menu-btn">Console</button>
                        <button onclick="window.dev.tools.showCheats()" class="dev-menu-btn">Cheats</button>
                        <button onclick="window.dev.tools.showPresetCharacters()" class="dev-menu-btn">Preset Characters</button>
                        <button onclick="window.dev.tools.showDataViewer()" class="dev-menu-btn">Data Viewer</button>
                        <button onclick="window.dev.tools.showGameState()" class="dev-menu-btn">Game State</button>
                        <button onclick="window.dev.tools.showPerformance()" class="dev-menu-btn">Performance</button>
                    </div>
                    
                    <div id="dev-content" style="
                        flex: 1;
                        padding: 10px;
                        overflow-y: auto;
                    ">
                        <div style="color: #888;">Select a menu option from the left</div>
                    </div>
                </div>
            </div>
            
            <style>
                .dev-menu-btn {
                    display: block;
                    width: 100%;
                    background: #333;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 8px;
                    margin: 3px 0;
                    cursor: pointer;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    border-radius: 3px;
                    transition: background 0.2s;
                }
                .dev-menu-btn:hover {
                    background: #004400;
                }
                .dev-console-input {
                    width: 100%;
                    background: #000;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 5px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }
                .dev-console-output {
                    background: #000;
                    color: #00ff00;
                    padding: 10px;
                    height: 300px;
                    overflow-y: auto;
                    border: 1px solid #00ff00;
                    margin-bottom: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    line-height: 1.3;
                }
            </style>
        `;
        
        document.body.insertAdjacentHTML('beforeend', menuHTML);
        this.isMenuOpen = true;
    }

    // Show console interface
    showConsole() {
        const content = document.getElementById('dev-content');
        content.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">DEVELOPER CONSOLE</div>
            <div id="console-output" class="dev-console-output">
                <div style="color: #888;">Developer Console - Type 'help' for available commands</div>
                ${this.consoleHistory.map(entry => `<div>${entry}</div>`).join('')}
            </div>
            <input type="text" id="console-input" class="dev-console-input" placeholder="Enter command..." onkeydown="window.dev.tools.handleConsoleInput(event)">
        `;
        
        // Focus the input
        setTimeout(() => {
            document.getElementById('console-input').focus();
        }, 100);
    }

    // Handle console input
    handleConsoleInput(event) {
        if (event.key === 'Enter') {
            const input = event.target.value.trim();
            if (input) {
                this.executeConsoleCommand(input);
                event.target.value = '';
            }
        }
    }

    // Execute console command
    executeConsoleCommand(commandLine) {
        const output = document.getElementById('console-output');
        
        // Add command to history
        this.consoleHistory.push(`> ${commandLine}`);
        output.innerHTML += `<div style="color: #ffff00;">> ${commandLine}</div>`;
        
        // Parse command
        const parts = commandLine.split(' ');
        const command = parts[0].toLowerCase();
        const args = parts.slice(1);
        
        try {
            if (this.commands[command]) {
                const result = this.commands[command].execute(args);
                if (result) {
                    this.consoleHistory.push(result);
                    output.innerHTML += `<div>${result}</div>`;
                }
            } else {
                const error = `Unknown command: ${command}. Type 'help' for available commands.`;
                this.consoleHistory.push(error);
                output.innerHTML += `<div style="color: #ff0000;">${error}</div>`;
            }
        } catch (error) {
            const errorMsg = `Error: ${error.message}`;
            this.consoleHistory.push(errorMsg);
            output.innerHTML += `<div style="color: #ff0000;">${errorMsg}</div>`;
        }
        
        output.scrollTop = output.scrollHeight;
    }

    // Show cheats interface
    showCheats() {
        const content = document.getElementById('dev-content');
        content.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">QUICK CHEATS</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <div style="margin-bottom: 5px; color: #888;">Character</div>
                    <button onclick="window.dev.tools.cheatAddGold(1000)" class="dev-menu-btn">+1000 Gold</button>
                    <button onclick="window.dev.tools.cheatHeal()" class="dev-menu-btn">Full Heal</button>
                    <button onclick="window.dev.tools.cheatSetLevel(10)" class="dev-menu-btn">Set Level 10</button>
                    <button onclick="window.dev.tools.cheatGodMode()" class="dev-menu-btn">Toggle God Mode</button>
                </div>
                <div>
                    <div style="margin-bottom: 5px; color: #888;">Game</div>
                    <button onclick="window.dev.tools.cheatTeleport('Village')" class="dev-menu-btn">Teleport to Village</button>
                    <button onclick="window.dev.tools.cheatTeleport('Dark Forest')" class="dev-menu-btn">Teleport to Forest</button>
                    <button onclick="window.dev.tools.reloadGameData()" class="dev-menu-btn">Reload Data</button>
                    <button onclick="window.dev.tools.resetGame()" class="dev-menu-btn">Reset Game</button>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <div style="margin-bottom: 5px; color: #888;">Custom Values</div>
                <div style="display: flex; gap: 10px; margin-bottom: 5px;">
                    <input type="number" id="custom-gold" placeholder="Gold amount" style="flex: 1; background: #000; color: #00ff00; border: 1px solid #00ff00; padding: 5px;">
                    <button onclick="window.dev.tools.cheatAddGold(parseInt(document.getElementById('custom-gold').value) || 0)" class="dev-menu-btn">Add Gold</button>
                </div>
                <div style="display: flex; gap: 10px;">
                    <input type="number" id="custom-level" placeholder="Level" style="flex: 1; background: #000; color: #00ff00; border: 1px solid #00ff00; padding: 5px;">
                    <button onclick="window.dev.tools.cheatSetLevel(parseInt(document.getElementById('custom-level').value) || 1)" class="dev-menu-btn">Set Level</button>
                </div>
            </div>
        `;
    }

    // Show data viewer
    showDataViewer(dataType = null) {
        const content = document.getElementById('dev-content');
        
        if (!dataType) {
            content.innerHTML = `
                <div style="margin-bottom: 10px; font-weight: bold;">DATA VIEWER</div>
                <div style="margin-bottom: 10px; color: #888;">Select data type to view:</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                    <button onclick="window.dev.tools.showDataViewer('races')" class="dev-menu-btn">Races</button>
                    <button onclick="window.dev.tools.showDataViewer('classes')" class="dev-menu-btn">Classes</button>
                    <button onclick="window.dev.tools.showDataViewer('backgrounds')" class="dev-menu-btn">Backgrounds</button>
                    <button onclick="window.dev.tools.showDataViewer('locations')" class="dev-menu-btn">Locations</button>
                    <button onclick="window.dev.tools.showDataViewer('enemies')" class="dev-menu-btn">Enemies</button>
                    <button onclick="window.dev.tools.showDataViewer('items')" class="dev-menu-btn">Items</button>
                    <button onclick="window.dev.tools.showDataViewer('shops')" class="dev-menu-btn">Shops</button>
                    <button onclick="window.dev.tools.showDataViewer('npcs')" class="dev-menu-btn">NPCs</button>
                    <button onclick="window.dev.tools.showDataViewer('rumors')" class="dev-menu-btn">Quests</button>
                    <button onclick="window.dev.tools.showDataViewer('quests')" class="dev-menu-btn">Rumors</button>
                </div>
            `;
            return;
        }

        let data = null;
        try {
            switch(dataType.toLowerCase()) {
                case 'races':
                    data = window.dataManager.data.races;
                    break;
                case 'classes':
                    data = window.dataManager.data.classes;
                    break;
                case 'backgrounds':
                    data = window.dataManager.data.backgrounds;
                    break;
                case 'locations':
                    data = window.dataManager.data.locations;
                    break;
                case 'enemies':
                    data = window.dataManager.data.enemies;
                    break;
                case 'items':
                    data = window.dataManager.data.items;
                    break;
                case 'shops':
                    data = window.dataManager.data.shops;
                    break;
                case 'npcs':
                    data = window.dataManager.data.npcs;
                    break;
                case 'rumors':
                    data = window.gameEngine.journal.rumors;
                    break;
                case 'quests':
                    data = window.gameEngine.journal.quests;
                    break;
                default:
                    throw new Error(`Unknown data type: ${dataType}`);
            }
        } catch (error) {
            content.innerHTML = `<div style="color: #ff0000;">Error loading data: ${error.message}</div>`;
            return;
        }

        content.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">DATA VIEWER - ${dataType.toUpperCase()}</div>
            <button onclick="window.dev.tools.showDataViewer()" class="dev-menu-btn" style="margin-bottom: 10px; width: 100px;">← Back</button>
            <pre style="
                background: #000;
                color: #00ff00;
                padding: 10px;
                border: 1px solid #00ff00;
                border-radius: 3px;
                overflow: auto;
                max-height: 350px;
                font-size: 10px;
                line-height: 1.2;
            ">${JSON.stringify(data, null, 2)}</pre>
        `;
    }

    // Show game state
    showGameState() {
        const content = document.getElementById('dev-content');
        const character = window.gameCharacter;
        const game = window.gameEngine;
        
        content.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">GAME STATE</div>
            <div style="font-size: 11px;">
                <div style="margin-bottom: 10px;">
                    <div style="color: #888;">Game Engine</div>
                    <div>State: ${game.gameState}</div>
                    <div>Location: ${game.currentLocation}</div>
                    <div>Loaded: ${game.gameLoaded}</div>
                </div>
                
                ${character ? `
                <div style="margin-bottom: 10px;">
                    <div style="color: #888;">Character</div>
                    <div>Name: ${character.name}</div>
                    <div>Level: ${character.level}</div>
                    <div>Health: ${character.health}/${character.maxHealth}</div>
                    <div>Gold: ${character.gold}</div>
                    <div>Location: ${character.location}</div>
                    <div>Race: ${character.race}</div>
                    <div>Class: ${character.characterClass}</div>
                </div>
                ` : '<div style="color: #888;">No character loaded</div>'}
                
                <div style="margin-bottom: 10px;">
                    <div style="color: #888;">Journal</div>
                    <div>Rumors: ${game.journal.rumors.length}</div>
                    <div>Quests: ${game.journal.quests.length}</div>
                </div>
                
                <div>
                    <div style="color: #888;">Audio</div>
                    <div>Music Enabled: ${window.audioManager ? window.audioManager.isMusicEnabled() : 'N/A'}</div>
                    <div>SFX Enabled: ${window.audioManager ? window.audioManager.isSFXEnabled() : 'N/A'}</div>
                </div>
            </div>
        `;
    }

    // Show performance info
    showPerformance() {
        const content = document.getElementById('dev-content');
        const memInfo = performance.memory ? {
            used: Math.round(performance.memory.usedJSHeapSize / 1048576),
            total: Math.round(performance.memory.totalJSHeapSize / 1048576),
            limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576)
        } : null;
        
        content.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">PERFORMANCE</div>
            <div style="font-size: 11px;">
                <div style="margin-bottom: 10px;">
                    <div style="color: #888;">Timing</div>
                    <div>Page Load: ${Math.round(performance.timing.loadEventEnd - performance.timing.navigationStart)}ms</div>
                    <div>DOM Ready: ${Math.round(performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart)}ms</div>
                </div>
                
                ${memInfo ? `
                <div style="margin-bottom: 10px;">
                    <div style="color: #888;">Memory (MB)</div>
                    <div>Used: ${memInfo.used}</div>
                    <div>Total: ${memInfo.total}</div>
                    <div>Limit: ${memInfo.limit}</div>
                </div>
                ` : ''}
                
                <div>
                    <div style="color: #888;">Browser</div>
                    <div>User Agent: ${navigator.userAgent}</div>
                    <div>Platform: ${navigator.platform}</div>
                    <div>Language: ${navigator.language}</div>
                </div>
            </div>
        `;
    }

    // Cheat functions
    cheatAddGold(amount) {
        if (!window.gameCharacter) return 'No character loaded';
        window.gameCharacter.addGold(amount);
        window.gameEngine.updateCharacterDisplay();
        return `Added ${amount} gold`;
    }

    cheatSetLevel(level) {
        if (!window.gameCharacter) return 'No character loaded';
        window.gameCharacter.level = Math.max(1, level);
        window.gameEngine.updateCharacterDisplay();
        return `Set level to ${level}`;
    }

    cheatHeal() {
        if (!window.gameCharacter) return 'No character loaded';
        window.gameCharacter.heal(window.gameCharacter.maxHealth);
        window.gameEngine.updateCharacterDisplay();
        return 'Character fully healed';
    }

    cheatGodMode() {
        if (!window.gameCharacter) return 'No character loaded';
        window.gameCharacter.godMode = !window.gameCharacter.godMode;
        return `God mode ${window.gameCharacter.godMode ? 'enabled' : 'disabled'}`;
    }

    cheatTeleport(location) {
        if (!location) return 'No location specified';
        if (!window.gameEngine) return 'Game engine not available';
        window.gameEngine.moveToLocation(location);
        return `Teleported to ${location}`;
    }

    // Utility functions
    showHelp() {
        const commandList = Object.entries(this.commands)
            .map(([cmd, info]) => `${cmd}: ${info.description}`)
            .join('\n');
        return `Available commands:\n${commandList}`;
    }

    clearConsole() {
        this.consoleHistory = [];
        const output = document.getElementById('console-output');
        if (output) {
            output.innerHTML = '<div style="color: #888;">Console cleared</div>';
        }
        return 'Console cleared';
    }

    reloadGameData() {
        if (window.dataManager) {
            window.dataManager.loadAllData();
            return 'Game data reloaded';
        }
        return 'Data manager not available';
    }

    resetGame() {
        if (confirm('Reset game to title screen?')) {
            window.gameEngine.showTitleScreen();
            this.closeMenu();
            return 'Game reset';
        }
        return 'Reset cancelled';
    }

    showDevHelp() {
        console.log(`
Developer Tools Help:
- Press \` to open/close developer menu
- Use window.dev object for console access
- Available dev functions:
  * dev.addGold(amount)
  * dev.setLevel(level)
  * dev.heal()
  * dev.godMode()
  * dev.showData(type)
  * dev.help()
        `);
    }

    // Load preset data from JSON file
    async loadPresetData() {
        try {
            const response = await fetch('./data/character_presets.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.presetData = data;
            console.log('Character presets loaded successfully');
        } catch (error) {
            console.error('Failed to load character presets:', error);
            this.presetData = []; // Fallback to empty array
        }
    }

    // Show preset characters interface
    showPresetCharacters() {
        const content = document.getElementById('dev-content');
        
        if (!this.presetData || this.presetData.length === 0) {
            content.innerHTML = `
                <div style="margin-bottom: 10px; font-weight: bold;">PRESET CHARACTERS</div>
                <div style="color: #ff6666;">Error: Could not load character presets. Check console for details.</div>
                <button onclick="window.dev.tools.loadPresetData().then(() => window.dev.tools.showPresetCharacters())" class="dev-menu-btn" style="margin-top: 10px;">Retry Loading</button>
            `;
            return;
        }

        let presetsHTML = '';
        this.presetData.forEach((preset, index) => {
            const classIcon = this.getClassIcon(preset.characterClass);
            const levelColor = preset.level >= 15 ? '#ff6600' : preset.level >= 10 ? '#ffaa00' : '#ffaa00';
            
            presetsHTML += `
                <div style="border: 1px solid #00ff00; padding: 10px; border-radius: 5px; background: #1a2a1a; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: bold; color: ${levelColor};">${classIcon} ${preset.name}</div>
                            <div style="color: #888; font-size: 11px;">${preset.gender} ${preset.race} ${preset.characterClass} - Level ${preset.level}</div>
                            <div style="color: #888; font-size: 10px; margin-top: 2px;">
                                STR: ${preset.attributes.strength}, DEX: ${preset.attributes.dexterity}, CON: ${preset.attributes.constitution}, 
                                INT: ${preset.attributes.intelligence}, WIS: ${preset.attributes.wisdom}, CHA: ${preset.attributes.charisma}
                            </div>
                            <div style="color: #888; font-size: 10px; margin-top: 2px;">
                                Gold: ${preset.gold} | Health: ${preset.health}/${preset.maxHealth}
                            </div>
                        </div>
                        <button onclick="window.dev.tools.loadPresetCharacterByIndex(${index})" class="dev-menu-btn" style="width: 80px;">Load</button>
                    </div>
                </div>
            `;
        });

        content.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: bold;">PRESET CHARACTERS</div>
            <div style="margin-bottom: 10px; color: #888;">Load pre-configured characters for testing:</div>
            
            <div style="max-height: 400px; overflow-y: auto;">
                ${presetsHTML}
            </div>
            
            <div style="margin-top: 15px; padding: 10px; background: #2a2a1a; border-radius: 5px; border: 1px solid #666;">
                <div style="color: #888; font-size: 11px;">
                    <strong>Note:</strong> Loading a preset character will replace your current character data. 
                    Make sure to save your current progress first if you want to keep it.
                </div>
            </div>
        `;
    }

    // Get class icon for display
    getClassIcon(characterClass) {
        const icons = {
            'Fighter': '⚔️',
            'Rogue': '🗡️',
            'Wizard': '🔮',
            'Cleric': '✨',
            'Ranger': '🏹',
            'Barbarian': '🪓',
            'Noble': '👑',
            'Witcher': '🐺'
        };
        return icons[characterClass] || '⚔️';
    }

    // Load preset character by index
    loadPresetCharacterByIndex(index) {
        if (!this.presetData || !this.presetData[index]) {
            return `Preset character at index ${index} not found.`;
        }

        const presetData = this.presetData[index];
        
        // Check if we're in the main menu or title screen and show warning
        if (window.gameEngine && (window.gameEngine.gameState === 'title' || window.gameEngine.gameState === 'character-creation')) {
            this.showPresetWarningDialog(index, presetData);
            return `Showing confirmation dialog for ${presetData.name}`;
        }
        
        // If we're already in-game, load directly
        this.actuallyLoadPresetCharacter(index, presetData);
        return `Loaded preset character: ${presetData.name}`;
    }

    // Load preset character data (updated to work with JSON data)
    loadPresetCharacter(presetName) {
        if (!this.presetData) {
            return 'Preset data not loaded. Please wait and try again.';
        }

        // Find preset by name (case-insensitive partial match)
        const preset = this.presetData.find(p => 
            p.name.toLowerCase().includes(presetName.toLowerCase()) ||
            p.characterClass.toLowerCase() === presetName.toLowerCase()
        );
        
        if (!preset) {
            return `Preset character "${presetName}" not found.`;
        }

        const index = this.presetData.indexOf(preset);
        return this.loadPresetCharacterByIndex(index);
    }

    // Show warning dialog for preset character loading
    showPresetWarningDialog(index, presetData) {
        if (!window.gameEngine || !window.gameEngine.showModal) {
            console.error('Game engine or modal system not available');
            return;
        }

        const warningHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="color: #ff6b6b; font-size: 18px; margin-bottom: 15px;">
                    ⚠️ Start New Game Warning ⚠️
                </div>
                <div style="margin-bottom: 20px; line-height: 1.6;">
                    <p>This will start a new game with <strong>${presetData.name}</strong>.</p>
                    <p style="color: #ffa500;">Any existing progress will be lost!</p>
                </div>
                <div style="display: flex; gap: 15px; justify-content: center; margin-top: 25px;">
                    <button onclick="window.developerTools.confirmPresetLoad(${index})" 
                            style="background: #e74c3c; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        Start New Game
                    </button>
                    <button onclick="window.gameEngine.closeModal()" 
                            style="background: #95a5a6; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        Cancel
                    </button>
                </div>
            </div>
        `;

        window.gameEngine.showModal(warningHTML, 'Load Preset Character');
    }

    // Confirm preset character load and start new game
    confirmPresetLoad(index) {
        // Close the modal first
        if (window.gameEngine && window.gameEngine.closeModal) {
            window.gameEngine.closeModal();
        }

        if (!this.presetData || !this.presetData[index]) {
            console.error(`Preset at index ${index} not found`);
            return;
        }

        const presetData = this.presetData[index];

        // Start a new game and then load the preset character
        if (window.gameEngine && window.gameEngine.startNewGame) {
            // Clear any existing save data
            localStorage.removeItem('legends_of_the_realm_save');
            
            // Start new game
            window.gameEngine.startNewGame();
            
            // Wait for character creation to initialize, then load preset
            setTimeout(() => {
                this.actuallyLoadPresetCharacter(index, presetData);
                
                // Skip character creation and go directly to game
                if (window.gameEngine) {
                    window.gameEngine.gameState = 'playing';
                    window.gameEngine.switchScreen('game-screen');
                    window.gameEngine.updateCharacterDisplay();
                    
                    // Play game music
                    if (window.audioManager && window.audioManager.playMusic) {
                        window.audioManager.playMusic('traveling');
                    }
                }
                
                console.log(`Started new game with preset character: ${presetData.name}`);
            }, 100);
        }
    }

    // Actually load the preset character data (updated to work with index)
    actuallyLoadPresetCharacter(index, presetData) {
        const character = window.gameCharacter;
        if (!character) {
            console.error('Game character not available');
            return;
        }

        // Load character data
        character.name = presetData.name;
        character.gender = presetData.gender;
        character.race = presetData.race;
        character.characterClass = presetData.characterClass;
        character.background = presetData.background;
        character.level = presetData.level;
        character.experience = presetData.experience;
        character.health = presetData.health;
        character.maxHealth = presetData.maxHealth;
        character.gold = presetData.gold;
        character.location = presetData.location;
        character.quests = presetData.quests || [];
        character.completedQuests = presetData.completedQuests || [];
        
        // Set attributes
        if (presetData.attributes) {
            character.attributes = { ...presetData.attributes };
        }
        
        // Set inventory
        character.inventory = [...(presetData.inventory || [])];
        
        // Set equipment
        if (presetData.equipment) {
            character.equipment = { ...presetData.equipment };
        }
        
        // Update display if we're in game
        if (window.gameEngine && window.gameEngine.updateCharacterDisplay) {
            window.gameEngine.updateCharacterDisplay();
        }
    }

    showMessage(message, type = 'info') {
        // Add to console output
        const output = document.getElementById('console-output');
        if (output) {
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'success' ? '#00ff00' : type === 'error' ? '#ff0000' : '#00ff00';
            output.innerHTML += `<div style="color: ${color};">[${timestamp}] ${message}</div>`;
            output.scrollTop = output.scrollHeight;
        }
        
        // Show in game if available
        if (window.gameEngine && window.gameEngine.showMessage) {
            window.gameEngine.showMessage(message, type);
        }
    }
}

// Initialize developer tools
window.developerTools = new DeveloperTools();
                location: "millhaven",
                inventory: ["Fine Wine", "Silk Clothes", "Trade Goods", "Merchant's Seal"],
                equipment: { weapon: "Ornate Dagger", armor: "Fine Clothes", accessory: "Gold Ring" },
                attributes: { strength: 10, dexterity: 14, constitution: 12, intelligence: 16, wisdom: 14, charisma: 18 },
                skills: {},
                quests: [],
                completedQuests: []
            }
        };
        
        const presetData = presets[preset];
        if (!presetData) {
            return `Preset character "${preset}" not found.`;
        }

        // Check if we're in the main menu or title screen and show warning
        if (window.gameEngine && (window.gameEngine.gameState === 'title' || window.gameEngine.gameState === 'character-creation')) {
            this.showPresetWarningDialog(preset, presetData);
            return `Showing confirmation dialog for ${presetData.name}`;
        }
        
        // If we're already in-game, load directly
        this.actuallyLoadPresetCharacter(preset, presetData);
        return `Loaded preset character: ${presetData.name}`;
    }

    // Show warning dialog for preset character loading
    showPresetWarningDialog(preset, presetData) {
        if (!window.gameEngine || !window.gameEngine.showModal) {
            console.error('Game engine or modal system not available');
            return;
        }

        const warningHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="color: #ff6b6b; font-size: 18px; margin-bottom: 15px;">
                    ⚠️ Start New Game Warning ⚠️
                </div>
                <div style="margin-bottom: 20px; line-height: 1.6;">
                    <p>This will start a new game with <strong>${presetData.name}</strong>.</p>
                    <p style="color: #ffa500;">Any existing progress will be lost!</p>
                </div>
                <div style="display: flex; gap: 15px; justify-content: center; margin-top: 25px;">
                    <button onclick="window.developerTools.confirmPresetLoad('${preset}')" 
                            style="background: #e74c3c; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        Start New Game
                    </button>
                    <button onclick="window.gameEngine.closeModal()" 
                            style="background: #95a5a6; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 14px;">
                        Cancel
                    </button>
                </div>
            </div>
        `;

        window.gameEngine.showModal(warningHTML, 'Load Preset Character');
    }

    // Confirm preset character load and start new game
    confirmPresetLoad(preset) {
        // Close the modal first
        if (window.gameEngine && window.gameEngine.closeModal) {
            window.gameEngine.closeModal();
        }

        // Get preset data again
        const presets = {
            warrior: { name: "Krolag the Mighty", gender: "Male", race: "Orc", characterClass: "Fighter", background: "Soldier", level: 3, experience: 150, health: 28, maxHealth: 28, gold: 500, location: "millhaven", inventory: ["Healing Potion", "Rations"], equipment: { weapon: "Iron Sword", armor: "Chainmail", accessory: null }, attributes: { strength: 18, dexterity: 14, constitution: 16, intelligence: 8, wisdom: 12, charisma: 10 }, skills: {}, quests: [], completedQuests: [] },
            rogue: { name: "Senna Shadowstep", gender: "Female", race: "Elf", characterClass: "Rogue", background: "Criminal", level: 3, experience: 150, health: 22, maxHealth: 22, gold: 750, location: "millhaven", inventory: ["Healing Potion", "Thieves' Tools", "Lockpicks"], equipment: { weapon: "Short Sword", armor: "Leather Armor", accessory: null }, attributes: { strength: 12, dexterity: 18, constitution: 14, intelligence: 14, wisdom: 16, charisma: 12 }, skills: {}, quests: [], completedQuests: [] },
            wizard: { name: "Thalion Starweaver", gender: "Male", race: "Human", characterClass: "Wizard", background: "Scholar", level: 3, experience: 150, health: 18, maxHealth: 18, gold: 300, location: "millhaven", inventory: ["Healing Potion", "Spellbook", "Component Pouch"], equipment: { weapon: "Staff", armor: "Robes", accessory: null }, attributes: { strength: 8, dexterity: 14, constitution: 14, intelligence: 18, wisdom: 16, charisma: 12 }, skills: {}, quests: [], completedQuests: [] },
            cleric: { name: "Lyra Dawnbringer", gender: "Female", race: "Dwarf", characterClass: "Cleric", background: "Acolyte", level: 3, experience: 150, health: 26, maxHealth: 26, gold: 400, location: "millhaven", inventory: ["Healing Potion", "Holy Symbol", "Prayer Book"], equipment: { weapon: "Mace", armor: "Scale Mail", accessory: null }, attributes: { strength: 14, dexterity: 10, constitution: 16, intelligence: 12, wisdom: 18, charisma: 14 }, skills: {}, quests: [], completedQuests: [] },
            ranger: { name: "Kael Windstrider", gender: "Male", race: "Halfling", characterClass: "Ranger", background: "Outlander", level: 3, experience: 150, health: 24, maxHealth: 24, gold: 350, location: "millhaven", inventory: ["Healing Potion", "Hunting Trap", "Survival Kit"], equipment: { weapon: "Longbow", armor: "Studded Leather", accessory: null }, attributes: { strength: 14, dexterity: 18, constitution: 14, intelligence: 12, wisdom: 16, charisma: 10 }, skills: {}, quests: [], completedQuests: [] },
            barbarian: { name: "Grok Ironbane", gender: "Male", race: "Orc", characterClass: "Barbarian", background: "Outlander", level: 3, experience: 150, health: 32, maxHealth: 32, gold: 200, location: "millhaven", inventory: ["Healing Potion", "Tribal Necklace"], equipment: { weapon: "Greataxe", armor: "Hide Armor", accessory: null }, attributes: { strength: 18, dexterity: 14, constitution: 18, intelligence: 8, wisdom: 12, charisma: 8 }, skills: {}, quests: [], completedQuests: [] },
            maxed: { name: "Maximus Testicus", gender: "Male", race: "Human", characterClass: "Fighter", background: "Noble", level: 20, experience: 15000, health: 200, maxHealth: 200, gold: 99999, location: "millhaven", inventory: ["Healing Potion", "Legendary Artifact", "Magic Ring", "Dragon Scale"], equipment: { weapon: "Legendary Sword", armor: "Plate Armor", accessory: "Ring of Power" }, attributes: { strength: 20, dexterity: 20, constitution: 20, intelligence: 20, wisdom: 20, charisma: 20 }, skills: {}, quests: [], completedQuests: [] },
            merchant: { name: "Goldbert Richman", gender: "Male", race: "Human", characterClass: "Noble", background: "Guild Merchant", level: 5, experience: 500, health: 30, maxHealth: 30, gold: 50000, location: "millhaven", inventory: ["Fine Wine", "Silk Clothes", "Trade Goods", "Merchant's Seal"], equipment: { weapon: "Ornate Dagger", armor: "Fine Clothes", accessory: "Gold Ring" }, attributes: { strength: 10, dexterity: 14, constitution: 12, intelligence: 16, wisdom: 14, charisma: 18 }, skills: {}, quests: [], completedQuests: [] }
        };

        const presetData = presets[preset];
        if (!presetData) {
            console.error(`Preset "${preset}" not found`);
            return;
        }

        // Start a new game and then load the preset character
        if (window.gameEngine && window.gameEngine.startNewGame) {
            // Clear any existing save data
            localStorage.removeItem('legends_of_the_realm_save');
            
            // Start new game
            window.gameEngine.startNewGame();
            
            // Wait for character creation to initialize, then load preset
            setTimeout(() => {
                this.actuallyLoadPresetCharacter(preset, presetData);
                
                // Skip character creation and go directly to game
                if (window.gameEngine) {
                    window.gameEngine.gameState = 'playing';
                    window.gameEngine.switchScreen('game-screen');
                    window.gameEngine.updateCharacterDisplay();
                    
                    // Play game music
                    if (window.audioManager && window.audioManager.playMusic) {
                        window.audioManager.playMusic('traveling');
                    }
                }
                
                console.log(`Started new game with preset character: ${presetData.name}`);
            }, 100);
        }
    }

    // Actually load the preset character data (separated for reuse)
    actuallyLoadPresetCharacter(preset, presetData) {
        const character = window.gameCharacter;
        if (!character) {
            console.error('Game character not available');
            return;
        }

        // Load character data
        character.name = presetData.name;
        character.gender = presetData.gender;
        character.race = presetData.race;
        character.characterClass = presetData.characterClass;
        character.background = presetData.background;
        character.level = presetData.level;
        character.experience = presetData.experience;
        character.health = presetData.health;
        character.maxHealth = presetData.maxHealth;
        character.gold = presetData.gold;
        character.location = presetData.location;
        character.quests = presetData.quests || [];
        character.completedQuests = presetData.completedQuests || [];
        
        // Set attributes
        if (presetData.attributes) {
            character.attributes = { ...presetData.attributes };
        }
        
        // Set inventory
        character.inventory = [...(presetData.inventory || [])];
        
        // Set equipment
        if (presetData.equipment) {
            character.equipment = { ...presetData.equipment };
        }
        
        // Update display if we're in game
        if (window.gameEngine && window.gameEngine.updateCharacterDisplay) {
            window.gameEngine.updateCharacterDisplay();
        }
    }

    showMessage(message, type = 'info') {
        // Add to console output
        const output = document.getElementById('console-output');
        if (output) {
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'success' ? '#00ff00' : type === 'error' ? '#ff0000' : '#00ff00';
            output.innerHTML += `<div style="color: ${color};">[${timestamp}] ${message}</div>`;
            output.scrollTop = output.scrollHeight;
        }
        
        // Show in game if available
        if (window.gameEngine && window.gameEngine.showMessage) {
            window.gameEngine.showMessage(message, type);
        }
    }
}

// Initialize developer tools
window.developerTools = new DeveloperTools();
