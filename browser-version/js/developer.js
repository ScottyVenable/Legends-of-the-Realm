// Developer tools and console system

class DeveloperTools {
    constructor() {
        this.isEnabled = false;
        this.isMenuOpen = false;
        this.consoleHistory = [];
        this.consoleHistoryIndex = -1;
        this.commands = {};
        
        this.setupCommands();
        this.setupKeyListener();
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
            }
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
}

// Initialize developer tools
window.developerTools = new DeveloperTools();
