// Quest Management System for Legends of the Realm
class QuestManager {
    constructor() {
        this.questDatabase = {}; // All available quests from quests.json
        this.playerQuests = new Map(); // Player's quest instances
    }

    // Initialize the quest manager with quest data
    async init() {
        try {
            const response = await fetch('data/quests.json');
            this.questDatabase = await response.json();
            console.log('Quest database loaded successfully');
        } catch (error) {
            console.error('Failed to load quest database:', error);
        }
    }

    // Create a player quest instance from the database
    createPlayerQuest(questId) {
        const questTemplate = this.questDatabase[questId];
        if (!questTemplate) {
            console.error(`Quest ${questId} not found in database`);
            return null;
        }

        // Create a copy of the quest with player-specific data
        const playerQuest = {
            ...JSON.parse(JSON.stringify(questTemplate)), // Deep copy
            status: 'active', // Override with player status
            dateAccepted: new Date().toISOString(),
            dateCompleted: null,
            playerProgress: {
                currentObjective: 0,
                objectivesCompleted: 0,
                completedObjectives: []
            }
        };

        return playerQuest;
    }

    // Add a quest to the player's quest log
    addQuest(questId) {
        if (this.playerQuests.has(questId)) {
            console.log(`Quest ${questId} already in player's quest log`);
            return false;
        }

        const playerQuest = this.createPlayerQuest(questId);
        if (!playerQuest) {
            return false;
        }

        this.playerQuests.set(questId, playerQuest);
        
        // Also add to character's quest array for backwards compatibility
        if (window.gameCharacter) {
            window.gameCharacter.quests.push({
                id: questId,
                status: 'active',
                progress: playerQuest.playerProgress
            });
        }

        console.log(`Quest added: ${playerQuest.name}`);
        return true;
    }

    // Update quest objective progress
    updateObjective(questId, objectiveId) {
        const quest = this.playerQuests.get(questId);
        if (!quest) {
            console.error(`Quest ${questId} not found in player quests`);
            return false;
        }

        const objective = quest.objectives.find(obj => obj.id === objectiveId);
        if (!objective) {
            console.error(`Objective ${objectiveId} not found in quest ${questId}`);
            return false;
        }

        if (objective.status === 'complete') {
            console.log(`Objective ${objectiveId} already completed`);
            return false;
        }

        // Mark objective as complete
        objective.status = 'complete';
        quest.playerProgress.completedObjectives.push(objectiveId);
        quest.playerProgress.objectivesCompleted++;

        // Update current objective to next incomplete one
        const nextObjective = quest.objectives.find(obj => obj.status === 'incomplete');
        if (nextObjective) {
            quest.playerProgress.currentObjective = nextObjective.id;
        } else {
            // All objectives complete, mark quest as available for completion
            quest.status = 'available_to_complete';
        }

        console.log(`Objective completed: ${objective.description}`);
        return true;
    }

    // Complete a quest
    completeQuest(questId) {
        const quest = this.playerQuests.get(questId);
        if (!quest) {
            console.error(`Quest ${questId} not found`);
            return false;
        }

        if (quest.status !== 'available_to_complete') {
            console.error(`Quest ${questId} is not available to complete`);
            return false;
        }

        quest.status = 'completed';
        quest.dateCompleted = new Date().toISOString();

        // Award rewards
        this.awardQuestRewards(quest);

        // Move from active to completed in character data
        if (window.gameCharacter) {
            const charQuestIndex = window.gameCharacter.quests.findIndex(q => q.id === questId);
            if (charQuestIndex !== -1) {
                const charQuest = window.gameCharacter.quests.splice(charQuestIndex, 1)[0];
                charQuest.status = 'completed';
                window.gameCharacter.completedQuests.push(charQuest);
            }
        }

        console.log(`Quest completed: ${quest.name}`);
        return true;
    }

    // Award quest rewards
    awardQuestRewards(quest) {
        if (!window.gameCharacter || !quest.rewards || !quest.rewards.completion) {
            return;
        }

        const rewards = quest.rewards.completion;
        
        // Award experience
        if (rewards.experience) {
            window.gameCharacter.experience += rewards.experience;
            console.log(`Gained ${rewards.experience} experience`);
        }

        // Award gold
        if (rewards.gold) {
            window.gameCharacter.gold += rewards.gold;
            console.log(`Gained ${rewards.gold} gold`);
        }

        // Award items
        if (rewards.items && Array.isArray(rewards.items)) {
            rewards.items.forEach(itemId => {
                // Add item to inventory (assuming inventory system exists)
                window.gameCharacter.inventory.push(itemId);
                console.log(`Received item: ${itemId}`);
            });
        }

        // Handle reputation changes
        if (rewards.reputation) {
            Object.entries(rewards.reputation).forEach(([faction, amount]) => {
                // Handle reputation system if it exists
                console.log(`Reputation with ${faction}: +${amount}`);
            });
        }
    }

    // Get quests by status
    getQuestsByStatus(status) {
        const quests = [];
        for (const [questId, quest] of this.playerQuests) {
            if (quest.status === status) {
                quests.push(quest);
            }
        }
        return quests;
    }

    // Get all player quests
    getAllPlayerQuests() {
        return Array.from(this.playerQuests.values());
    }

    // Get quest by ID
    getQuest(questId) {
        return this.playerQuests.get(questId);
    }

    // Check if player has quest
    hasQuest(questId) {
        return this.playerQuests.has(questId);
    }

    // Get current objective for a quest
    getCurrentObjective(questId) {
        const quest = this.playerQuests.get(questId);
        if (!quest) return null;

        return quest.objectives.find(obj => obj.id === quest.playerProgress.currentObjective);
    }

    // Save quest data to character
    saveToCharacter() {
        if (!window.gameCharacter) return;

        // Convert quest map to array for storage
        const questArray = Array.from(this.playerQuests.entries()).map(([id, quest]) => ({
            id,
            status: quest.status,
            progress: quest.playerProgress,
            dateAccepted: quest.dateAccepted,
            dateCompleted: quest.dateCompleted
        }));

        window.gameCharacter.questData = questArray;
    }

    // Load quest data from character
    loadFromCharacter() {
        if (!window.gameCharacter || !window.gameCharacter.questData) return;

        window.gameCharacter.questData.forEach(savedQuest => {
            const questTemplate = this.questDatabase[savedQuest.id];
            if (questTemplate) {
                const playerQuest = {
                    ...JSON.parse(JSON.stringify(questTemplate)),
                    status: savedQuest.status,
                    dateAccepted: savedQuest.dateAccepted,
                    dateCompleted: savedQuest.dateCompleted,
                    playerProgress: savedQuest.progress
                };

                // Update objective statuses based on progress
                playerQuest.objectives.forEach(obj => {
                    if (savedQuest.progress.completedObjectives.includes(obj.id)) {
                        obj.status = 'complete';
                    }
                });

                this.playerQuests.set(savedQuest.id, playerQuest);
            }
        });
    }
}

// Global quest manager instance
window.questManager = new QuestManager();
