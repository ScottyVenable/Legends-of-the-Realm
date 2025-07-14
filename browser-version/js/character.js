// Character creation and management system
class Character {
    constructor() {
        this.name = '';
        this.gender = '';
        this.race = '';
        this.characterClass = '';
        this.background = '';
        this.level = 1;
        this.experience = 0;
        this.health = 10;
        this.maxHealth = 10;
        this.gold = 10;
        this.location = 'millhaven';
        this.inventory = [];
        this.equipment = {
            weapon: null,
            armor: null,
            accessory: null
        };
        this.attributes = {
            strength: 10,
            dexterity: 10,
            constitution: 10,
            intelligence: 10,
            wisdom: 10,
            charisma: 10
        };
        this.skills = {};
        this.quests = [];
        this.completedQuests = [];
    }

    // Create character from form data
    static createFromForm() {
        const character = new Character();
        
        character.name = document.getElementById('character-name').value;
        character.gender = document.querySelector('input[name="gender"]:checked')?.value || '';
        character.race = document.getElementById('race-select').value;
        character.characterClass = document.getElementById('class-select').value;
        character.background = document.getElementById('background-select').value;

        // Get attributes based on method
        const statMethod = document.querySelector('input[name="stat-method"]:checked')?.value;
        if (statMethod === 'pointbuy') {
            character.getPointBuyAttributes();
        } else {
            character.getRolledAttributes();
        }

        // Apply racial bonuses
        character.applyRacialBonuses();
        
        // Calculate derived stats
        character.calculateDerivedStats();
        
        // Add starting equipment
        character.addStartingEquipment();

        return character;
    }

    // Get rolled attributes from UI
    getRolledAttributes() {
        const results = document.getElementById('attribute-results');
        if (results && results.dataset.attributes) {
            const attrs = JSON.parse(results.dataset.attributes);
            this.attributes = { ...attrs };
        }
    }

    // Get point buy attributes from UI
    getPointBuyAttributes() {
        const controls = document.getElementById('pointbuy-controls');
        if (controls) {
            const inputs = controls.querySelectorAll('input[type="number"]');
            inputs.forEach(input => {
                const attr = input.dataset.attribute;
                if (attr) {
                    this.attributes[attr] = parseInt(input.value) || 10;
                }
            });
        }
    }

    // Apply racial attribute bonuses
    applyRacialBonuses() {
        const raceData = window.dataManager.getRace(this.race);
        if (raceData && raceData.attributes) {
            for (const [attr, bonus] of Object.entries(raceData.attributes)) {
                if (this.attributes.hasOwnProperty(attr)) {
                    this.attributes[attr] += bonus;
                }
            }
        }
    }

    // Calculate derived stats (health, AC, etc.)
    calculateDerivedStats() {
        const classData = window.dataManager.getClass(this.characterClass);
        const conModifier = this.getAttributeModifier('constitution');
        
        // Calculate max health
        const baseHealth = classData?.hit_die || 8;
        this.maxHealth = baseHealth + conModifier;
        this.health = this.maxHealth;

        // Calculate Armor Class (base 10 + Dex modifier)
        this.ac = 10 + this.getAttributeModifier('dexterity');

        // Starting gold based on background
        const backgroundData = window.dataManager.getBackground(this.background);
        if (backgroundData && backgroundData.starting_gold) {
            this.gold = backgroundData.starting_gold;
        }
        
        // Set class proficiencies
        if (classData && classData.proficiencies) {
            this.skills = { ...this.skills, ...classData.proficiencies };
        }
        
        // Set background proficiencies
        if (backgroundData && backgroundData.proficiencies) {
            this.skills = { ...this.skills, ...backgroundData.proficiencies };
        }
    }

    // Add starting equipment based on class and background
    addStartingEquipment() {
        const classData = window.dataManager.getClass(this.characterClass);
        const backgroundData = window.dataManager.getBackground(this.background);

        // Add class starting equipment
        if (classData && classData.starting_equipment) {
            classData.starting_equipment.forEach(itemName => {
                this.addItem(itemName);
            });
        }

        // Add background starting equipment
        if (backgroundData && backgroundData.starting_equipment) {
            backgroundData.starting_equipment.forEach(itemName => {
                this.addItem(itemName);
            });
        }
    }

    // Get attribute modifier (-5 to +5)
    getAttributeModifier(attributeName) {
        const score = this.attributes[attributeName] || 10;
        return Math.floor((score - 10) / 2);
    }

    // Calculate Armor Class
    getArmorClass() {
        let ac = 10 + this.getAttributeModifier('dexterity');
        
        // Add armor bonus if equipped
        if (this.equipment.armor) {
            const armorData = window.dataManager.getItem(this.equipment.armor);
            if (armorData && armorData.ac_bonus) {
                ac += armorData.ac_bonus;
            }
        }
        
        return ac;
    }

    // Attack roll calculation
    getAttackBonus() {
        let bonus = this.getAttributeModifier('strength');
        
        // Add weapon attack bonus if equipped
        if (this.equipment.weapon) {
            const weaponData = window.dataManager.getItem(this.equipment.weapon);
            if (weaponData && weaponData.attack_bonus) {
                bonus += weaponData.attack_bonus;
            }
        }
        
        return bonus;
    }

    // Damage roll calculation
    getDamageRoll() {
        let baseDamage = '1d4'; // Default unarmed damage
        let bonus = this.getAttributeModifier('strength');
        
        if (this.equipment.weapon) {
            const weaponData = window.dataManager.getItem(this.equipment.weapon);
            if (weaponData && weaponData.damage) {
                baseDamage = weaponData.damage;
            }
        }
        
        return { dice: baseDamage, bonus: bonus };
    }

    // Add item to inventory
    addItem(itemName, quantity = 1) {
        const existingItem = this.inventory.find(item => item.name === itemName);
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.inventory.push({
                name: itemName,
                quantity: quantity
            });
        }
    }

    // Remove item from inventory
    removeItem(itemName, quantity = 1) {
        const itemIndex = this.inventory.findIndex(item => item.name === itemName);
        if (itemIndex !== -1) {
            this.inventory[itemIndex].quantity -= quantity;
            if (this.inventory[itemIndex].quantity <= 0) {
                this.inventory.splice(itemIndex, 1);
            }
            return true;
        }
        return false;
    }

    // Equip an item
    equipItem(itemName) {
        const itemData = window.dataManager.getItem(itemName);
        if (!itemData) return false;

        const slot = itemData.slot;
        if (!slot || !this.equipment.hasOwnProperty(slot)) return false;

        // Unequip current item in slot
        if (this.equipment[slot]) {
            this.addItem(this.equipment[slot]);
        }

        // Equip new item
        this.equipment[slot] = itemName;
        this.removeItem(itemName, 1);
        
        return true;
    }

    // Unequip an item
    unequipItem(slot) {
        if (this.equipment[slot]) {
            this.addItem(this.equipment[slot]);
            this.equipment[slot] = null;
            return true;
        }
        return false;
    }

    // Take damage
    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        return this.health <= 0; // Returns true if character dies
    }

    // Heal damage
    heal(amount) {
        this.health = Math.min(this.maxHealth, this.health + amount);
    }

    // Add experience and handle level up
    addExperience(amount) {
        this.experience += amount;
        
        // Check for level up (simple formula: level * 100 XP per level)
        const xpNeeded = this.level * 100;
        if (this.experience >= xpNeeded) {
            this.levelUp();
        }
    }

    // Level up character
    levelUp() {
        this.level++;
        this.experience = 0; // Reset XP for next level
        
        // Increase max health
        const classData = window.dataManager.getClass(this.characterClass);
        const conModifier = this.getAttributeModifier('constitution');
        const healthGain = Math.max(1, Math.floor((classData?.hit_die || 8) / 2) + conModifier);
        
        this.maxHealth += healthGain;
        this.health = this.maxHealth; // Full heal on level up
        
        console.log(`${this.name} leveled up to level ${this.level}!`);
        return healthGain;
    }

    // Add quest to active quests
    addQuest(questName) {
        if (!this.quests.includes(questName)) {
            this.quests.push(questName);
        }
    }

    // Complete a quest
    completeQuest(questName) {
        const questIndex = this.quests.indexOf(questName);
        if (questIndex !== -1) {
            this.quests.splice(questIndex, 1);
            this.completedQuests.push(questName);
            
            // Award quest rewards
            const questData = window.dataManager.getQuest(questName);
            if (questData) {
                if (questData.gold_reward) {
                    this.gold += questData.gold_reward;
                }
                if (questData.xp_reward) {
                    this.addExperience(questData.xp_reward);
                }
                if (questData.item_reward) {
                    this.addItem(questData.item_reward);
                }
            }
            
            return true;
        }
        return false;
    }

    // Check if character has enough gold
    canAfford(cost) {
        return this.gold >= cost;
    }

    // Spend gold
    spendGold(amount) {
        if (this.canAfford(amount)) {
            this.gold -= amount;
            return true;
        }
        return false;
    }

    // Add gold
    addGold(amount) {
        this.gold += Math.max(0, amount);
    }

    // Use item (consumables, equippables)
    useItem(itemName) {
        const itemData = window.dataManager.getItem(itemName);
        if (!itemData) return false;

        if (itemData.type === 'consumable') {
            if (itemData.effect === 'heal') {
                const healAmount = itemData.value || 10;
                this.heal(healAmount);
                this.removeItem(itemName, 1);
                return { success: true, message: `You used ${itemName} and healed ${healAmount} health.` };
            }
        } else if (itemData.type === 'weapon' || itemData.type === 'armor') {
            return this.equipItem(itemName);
        }
        
        return { success: false, message: `You can't use ${itemName}.` };
    }

    // Get character summary for display
    getSummary() {
        const raceData = window.dataManager.getRace(this.race);
        const classData = window.dataManager.getClass(this.characterClass);
        const backgroundData = window.dataManager.getBackground(this.background);

        return {
            name: this.name,
            title: `${this.race} ${this.characterClass}`,
            level: this.level,
            health: this.health,
            maxHealth: this.maxHealth,
            gold: this.gold,
            location: this.location,
            attributes: { ...this.attributes },
            race: raceData?.name || this.race,
            characterClass: classData?.name || this.characterClass,
            background: backgroundData?.name || this.background
        };
    }

    // Serialize character for saving
    toJSON() {
        return {
            name: this.name,
            gender: this.gender,
            race: this.race,
            characterClass: this.characterClass,
            background: this.background,
            level: this.level,
            experience: this.experience,
            health: this.health,
            maxHealth: this.maxHealth,
            gold: this.gold,
            location: this.location,
            inventory: [...this.inventory],
            equipment: { ...this.equipment },
            attributes: { ...this.attributes },
            skills: { ...this.skills },
            quests: [...this.quests],
            completedQuests: [...this.completedQuests]
        };
    }

    // Convert character to save-friendly object
    toSaveObject() {
        return {
            name: this.name,
            gender: this.gender,
            race: this.race,
            characterClass: this.characterClass,
            background: this.background,
            level: this.level,
            experience: this.experience,
            health: this.health,
            maxHealth: this.maxHealth,
            gold: this.gold,
            location: this.location,
            inventory: this.inventory,
            equipment: this.equipment,
            attributes: this.attributes,
            skills: this.skills,
            quests: this.quests,
            completedQuests: this.completedQuests
        };
    }

    // Create character from saved object
    static fromSaveObject(saveData) {
        const character = new Character();
        
        // Restore all properties
        character.name = saveData.name || '';
        character.gender = saveData.gender || '';
        character.race = saveData.race || '';
        character.characterClass = saveData.characterClass || '';
        character.background = saveData.background || '';
        character.level = saveData.level || 1;
        character.experience = saveData.experience || 0;
        character.health = saveData.health || 10;
        character.maxHealth = saveData.maxHealth || 10;
        character.gold = saveData.gold || 10;
        character.location = saveData.location || 'millhaven';
        
        // Handle legacy location names
        if (character.location === 'Village' || character.location === 'Millhaven') {
            character.location = 'millhaven';
        } else if (character.location === 'Forest Path') {
            character.location = 'forest_path';
        } else if (character.location === 'Goblin Camp') {
            character.location = 'goblin_camp';
        } else if (character.location === 'Bandit Lair') {
            character.location = 'bandit_lair';
        } else if (character.location === 'Capital City') {
            character.location = 'capital_city';
        } else if (character.location === 'Mountain Pass') {
            character.location = 'mountain_pass';
        } else if (character.location === "Dragon's Lair") {
            character.location = 'dragons_lair';
        }
        character.inventory = saveData.inventory || [];
        character.equipment = saveData.equipment || { weapon: null, armor: null, accessory: null };
        character.attributes = saveData.attributes || {
            strength: 10, dexterity: 10, constitution: 10,
            intelligence: 10, wisdom: 10, charisma: 10
        };
        character.skills = saveData.skills || {};
        character.quests = saveData.quests || [];
        character.completedQuests = saveData.completedQuests || [];

        return character;
    }

    // Load character from JSON data
    static fromJSON(data) {
        const character = new Character();
        Object.assign(character, data);
        return character;
    }

    // Validate character is properly created
    isValid() {
        return this.name && this.race && this.characterClass && this.background;
    }
}

// Character creation helper functions
class CharacterCreator {
    static rollAttributes() {
        const attributes = {};
        const attributeNames = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
        
        attributeNames.forEach(attr => {
            // Roll 4d6, drop lowest
            const rolls = [];
            for (let i = 0; i < 4; i++) {
                rolls.push(Math.floor(Math.random() * 6) + 1);
            }
            rolls.sort((a, b) => b - a);
            attributes[attr] = rolls.slice(0, 3).reduce((sum, roll) => sum + roll, 0);
        });
        
        return attributes;
    }

    static displayRolledAttributes(attributes) {
        const container = document.getElementById('attribute-results');
        if (!container) return;

        container.dataset.attributes = JSON.stringify(attributes);
        
        let html = '<div class="rolled-stats">';
        for (const [attr, value] of Object.entries(attributes)) {
            const modifier = Math.floor((value - 10) / 2);
            const modStr = modifier >= 0 ? `+${modifier}` : `${modifier}`;
            html += `
                <div class="stat-block">
                    <strong>${attr.charAt(0).toUpperCase() + attr.slice(1)}:</strong> 
                    ${value} (${modStr})
                </div>
            `;
        }
        html += '</div>';
        
        container.innerHTML = html;
    }

    static setupPointBuy() {
        const container = document.getElementById('pointbuy-controls');
        if (!container) return;

        const attributeNames = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'];
        let html = '';
        
        attributeNames.forEach(attr => {
            html += `
                <div class="pointbuy-row">
                    <label>${attr.charAt(0).toUpperCase() + attr.slice(1)}:</label>
                    <button onclick="CharacterCreator.adjustAttribute('${attr}', -1)">-</button>
                    <input type="number" value="10" min="8" max="15" data-attribute="${attr}" onchange="CharacterCreator.updatePointBuy()">
                    <button onclick="CharacterCreator.adjustAttribute('${attr}', 1)">+</button>
                    <span class="modifier" id="${attr}-modifier">+0</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
        this.updatePointBuy();
    }

    static adjustAttribute(attributeName, change) {
        const input = document.querySelector(`input[data-attribute="${attributeName}"]`);
        if (!input) return;
        
        const currentValue = parseInt(input.value);
        const newValue = Math.max(8, Math.min(15, currentValue + change));
        input.value = newValue;
        
        this.updatePointBuy();
    }

    static updatePointBuy() {
        const inputs = document.querySelectorAll('#pointbuy-controls input[data-attribute]');
        let totalCost = 0;
        
        inputs.forEach(input => {
            const value = parseInt(input.value);
            const attr = input.dataset.attribute;
            
            // Point buy cost: 8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9
            const costs = [0, 1, 2, 3, 4, 5, 7, 9];
            const cost = costs[value - 8] || 0;
            totalCost += cost;
            
            // Update modifier display
            const modifier = Math.floor((value - 10) / 2);
            const modStr = modifier >= 0 ? `+${modifier}` : `${modifier}`;
            const modDisplay = document.getElementById(`${attr}-modifier`);
            if (modDisplay) {
                modDisplay.textContent = modStr;
            }
        });
        
        const remaining = 27 - totalCost;
        const remainingDisplay = document.getElementById('points-remaining');
        if (remainingDisplay) {
            remainingDisplay.textContent = remaining;
            remainingDisplay.style.color = remaining < 0 ? '#ff6666' : '#66ff66';
        }
        
        // Enable/disable buttons based on remaining points and limits
        inputs.forEach(input => {
            const value = parseInt(input.value);
            const attr = input.dataset.attribute;
            const row = input.closest('.pointbuy-row');
            const minusBtn = row.querySelector('button:first-of-type');
            const plusBtn = row.querySelector('button:last-of-type');
            
            minusBtn.disabled = value <= 8;
            plusBtn.disabled = value >= 15 || remaining <= 0;
        });
    }
}

// Global functions for HTML
function rollAttributes() {
    const attributes = CharacterCreator.rollAttributes();
    CharacterCreator.displayRolledAttributes(attributes);
    checkFormCompletion();
}

function checkFormCompletion() {
    const name = document.getElementById('character-name').value;
    const gender = document.querySelector('input[name="gender"]:checked');
    const race = document.getElementById('race-select').value;
    const characterClass = document.getElementById('class-select').value;
    const background = document.getElementById('background-select').value;
    
    const createBtn = document.getElementById('create-btn');
    const isComplete = name && gender && race && characterClass && background;
    
    if (createBtn) {
        createBtn.disabled = !isComplete;
    }
}

// Global character instance
window.gameCharacter = null;
