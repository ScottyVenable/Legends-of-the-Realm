// Data loading and management system
class DataManager {
    constructor() {
        this.gameData = {
            races: null,
            classes: null,
            backgrounds: null,
            items: null,
            locations: null,
            enemies: null,
            npcs: null,
            quests: null,
            shops: null,
            dialogues: null,
            gameinfo: null
        };
        this.loaded = false;
    }

    // Load all game data from JSON files
    async loadAllData() {
        console.log('Loading game data...');
        
        try {
            const dataFiles = [
                'races.json',
                'classes.json', 
                'backgrounds.json',
                'items.json',
                'locations.json',
                'enemies.json',
                'npcs.json',
                'quests.json',
                'shops.json',
                'dialogues.json',
                'gameinfo.json'
            ];

            const promises = dataFiles.map(file => this.loadJSON(`data/${file}`));
            const results = await Promise.all(promises);

            // Map results to data object
            this.gameData.races = results[0];
            this.gameData.classes = results[1];
            this.gameData.backgrounds = results[2];
            this.gameData.items = results[3];
            this.gameData.locations = results[4];
            this.gameData.enemies = results[5];
            this.gameData.npcs = results[6];
            this.gameData.quests = results[7];
            this.gameData.shops = results[8];
            this.gameData.dialogues = results[9];
            this.gameData.gameinfo = results[10];

            this.loaded = true;
            console.log('All game data loaded successfully');
            return true;

        } catch (error) {
            console.error('Error loading game data:', error);
            this.showError('Failed to load game data. Please refresh the page.');
            return false;
        }
    }

    // Load a single JSON file
    async loadJSON(filepath) {
        try {
            const response = await fetch(filepath);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error loading ${filepath}:`, error);
            throw error;
        }
    }

    // Get race data by race name
    getRace(raceName) {
        if (!this.gameData.races || !this.gameData.races[raceName]) {
            console.warn(`Race '${raceName}' not found`);
            return null;
        }
        return this.gameData.races[raceName];
    }

    // Get class data by class name
    getClass(className) {
        if (!this.gameData.classes || !this.gameData.classes[className]) {
            console.warn(`Class '${className}' not found`);
            return null;
        }
        return this.gameData.classes[className];
    }

    // Get background data by background name
    getBackground(backgroundName) {
        if (!this.gameData.backgrounds || !this.gameData.backgrounds[backgroundName]) {
            console.warn(`Background '${backgroundName}' not found`);
            return null;
        }
        return this.gameData.backgrounds[backgroundName];
    }

    // Get location data by location name
    getLocation(locationName) {
        if (!this.gameData.locations || !this.gameData.locations[locationName]) {
            console.warn(`Location '${locationName}' not found`);
            return null;
        }
        return this.gameData.locations[locationName];
    }

    // Get item data by item name
    getItem(itemName) {
        if (!this.gameData.items) {
            console.warn('Items data not loaded');
            return null;
        }
        
        // Handle flat item structure (items.json has items directly)
        if (this.gameData.items[itemName]) {
            return this.gameData.items[itemName];
        }
        
        // Fallback: Search through categorized items if structure is different
        for (const category in this.gameData.items) {
            if (this.gameData.items[category][itemName]) {
                return this.gameData.items[category][itemName];
            }
        }
        
        console.warn(`Item '${itemName}' not found`);
        return null;
    }

    // Get shop data with day-based randomized sales
    getShop(shopName) {
        if (!this.gameData.shops || !this.gameData.shops[shopName]) {
            console.warn(`Shop '${shopName}' not found`);
            return null;
        }
        
        // Get current game day from gameEngine
        const currentDay = window.gameEngine ? window.gameEngine.gameDay : 1;
        const cacheKey = `${shopName}_day_${currentDay}`;
        
        // Check if we have cached sales for this shop and day
        if (window.gameEngine && window.gameEngine.shopSalesCache[cacheKey]) {
            return window.gameEngine.shopSalesCache[cacheKey];
        }
        
        // Clone the shop data to avoid modifying the original
        const shopData = JSON.parse(JSON.stringify(this.gameData.shops[shopName]));
        
        // Randomize sales for this day
        this.randomizeShopSales(shopData, currentDay);
        
        // Cache the shop data for this day
        if (window.gameEngine) {
            window.gameEngine.shopSalesCache[cacheKey] = shopData;
        }
        
        return shopData;
    }

    // Randomize which items are on sale and their discount percentages based on day
    randomizeShopSales(shopData, gameDay) {
        if (!shopData.inventory) return;
        
        // Use gameDay as seed for consistent randomization per day
        const dayRandom = this.seededRandom(gameDay + shopData.merchant_name.length);
        
        const inventoryItems = Object.keys(shopData.inventory);
        const numItemsOnSale = Math.floor(dayRandom() * 3) + 1; // 1-3 items on sale
        
        // Reset all sales first
        Object.values(shopData.inventory).forEach(item => {
            item.on_sale = false;
            item.discount = 0;
        });
        
        // Randomly select items to put on sale using seeded random
        const shuffledItems = [...inventoryItems].sort(() => dayRandom() - 0.5);
        const itemsToSale = shuffledItems.slice(0, numItemsOnSale);
        
        itemsToSale.forEach(itemName => {
            const item = shopData.inventory[itemName];
            item.on_sale = true;
            // Random discount between 10% and 40% using seeded random
            item.discount = Math.floor(dayRandom() * 31) + 10;
        });
    }

    // Seeded random number generator for consistent daily sales
    seededRandom(seed) {
        let currentSeed = seed;
        return function() {
            currentSeed = (currentSeed * 9301 + 49297) % 233280;
            return currentSeed / 233280;
        };
    }

    // Get NPC data by NPC name
    getNPC(npcName) {
        if (!this.gameData.npcs || !this.gameData.npcs[npcName]) {
            console.warn(`NPC '${npcName}' not found`);
            return null;
        }
        return this.gameData.npcs[npcName];
    }

    // Get enemy data by enemy name
    getEnemy(enemyName) {
        if (!this.gameData.enemies || !this.gameData.enemies[enemyName]) {
            console.warn(`Enemy '${enemyName}' not found`);
            return null;
        }
        return this.gameData.enemies[enemyName];
    }

    // Get dialogue data by dialogue ID
    getDialogue(dialogueId) {
        if (!this.gameData.dialogues || !this.gameData.dialogues[dialogueId]) {
            console.warn(`Dialogue '${dialogueId}' not found`);
            return null;
        }
        return this.gameData.dialogues[dialogueId];
    }

    // Get quest data by quest name
    getQuest(questName) {
        if (!this.gameData.quests || !this.gameData.quests[questName]) {
            console.warn(`Quest '${questName}' not found`);
            return null;
        }
        return this.gameData.quests[questName];
    }

    // Get all available races
    getAllRaces() {
        return this.gameData.races ? Object.keys(this.gameData.races) : [];
    }

    // Get all available classes
    getAllClasses() {
        return this.gameData.classes ? Object.keys(this.gameData.classes) : [];
    }

    // Get all available backgrounds
    getAllBackgrounds() {
        return this.gameData.backgrounds ? Object.keys(this.gameData.backgrounds) : [];
    }

    // Get all locations
    getAllLocations() {
        return this.gameData.locations ? Object.keys(this.gameData.locations) : [];
    }

    // Get game info
    getGameInfo() {
        return this.gameData.gameinfo || {};
    }

    // Check if data is loaded
    isLoaded() {
        return this.loaded;
    }

    // Show error message to user
    showError(message) {
        // Create error dialog
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #8b0000;
            color: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #ff0000;
            z-index: 10000;
            text-align: center;
            font-family: 'Cinzel', serif;
        `;
        errorDiv.innerHTML = `
            <h3>Error</h3>
            <p>${message}</p>
            <button onclick="this.parentElement.remove()" style="
                background: #660000;
                color: white;
                border: 1px solid #ff0000;
                padding: 8px 16px;
                margin-top: 10px;
                cursor: pointer;
                border-radius: 4px;
            ">OK</button>
        `;
        document.body.appendChild(errorDiv);
    }

    // Utility method to get random item from array
    getRandomItem(array) {
        if (!array || array.length === 0) return null;
        return array[Math.floor(Math.random() * array.length)];
    }

    // Utility method to roll dice
    rollDice(sides, count = 1) {
        let total = 0;
        for (let i = 0; i < count; i++) {
            total += Math.floor(Math.random() * sides) + 1;
        }
        return total;
    }

    // Validate required data is loaded
    validateData() {
        const requiredData = ['races', 'classes', 'backgrounds', 'locations'];
        const missing = [];
        
        for (const dataType of requiredData) {
            if (!this.gameData[dataType]) {
                missing.push(dataType);
            }
        }
        
        if (missing.length > 0) {
            console.error('Missing required data:', missing);
            return false;
        }
        
        return true;
    }
}

// Create global data manager instance
window.dataManager = new DataManager();
