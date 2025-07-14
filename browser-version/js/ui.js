// UI utilities and helper functions
class UIManager {
    constructor() {
        this.activeModal = null;
        this.messageQueue = [];
        this.isShowingMessage = false;
    }

    // Initialize UI event listeners
    init() {
        // Setup modal close on overlay click
        const modalOverlay = document.getElementById('modal-overlay');
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    window.gameEngine.closeModal();
                }
            });
        }

        // Setup keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyPress(e);
        });

        // Setup form validation
        this.setupFormValidation();

        // Setup responsive menu for mobile
        this.setupResponsiveUI();

        console.log('UI Manager initialized');
    }

    // Handle keyboard shortcuts
    handleKeyPress(event) {
        // Don't interfere with form inputs
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        switch (event.key) {
            case 'Escape':
                event.preventDefault();
                this.handleEscape();
                break;
            case 'Enter':
                event.preventDefault();
                this.handleEnter();
                break;
            case 'i':
            case 'I':
                if (window.gameCharacter && window.gameEngine.gameState === 'playing') {
                    event.preventDefault();
                    showInventory();
                }
                break;
            case 'c':
            case 'C':
                if (window.gameCharacter && window.gameEngine.gameState === 'playing') {
                    event.preventDefault();
                    showCharacterSheet();
                }
                break;
            case 's':
            case 'S':
                if (event.ctrlKey && window.gameCharacter) {
                    event.preventDefault();
                    saveGame();
                }
                break;
        }
    }

    // Handle escape key
    handleEscape() {
        const modal = document.getElementById('modal-overlay');
        if (modal && modal.classList.contains('active')) {
            window.gameEngine.closeModal();
        }
    }

    // Handle enter key
    handleEnter() {
        const activeElement = document.activeElement;
        if (activeElement && activeElement.tagName === 'BUTTON') {
            activeElement.click();
        }
    }

    // Setup form validation
    setupFormValidation() {
        // Character name validation
        const nameInput = document.getElementById('character-name');
        if (nameInput) {
            nameInput.addEventListener('input', (e) => {
                const value = e.target.value;
                const isValid = value.length >= 2 && value.length <= 20 && /^[a-zA-Z\s]+$/.test(value);
                
                if (!isValid && value.length > 0) {
                    e.target.style.borderColor = '#ff6666';
                } else {
                    e.target.style.borderColor = '#8b4513';
                }
            });
        }

        // Real-time form validation for character creation
        const formInputs = document.querySelectorAll('#character-creation input, #character-creation select');
        formInputs.forEach(input => {
            input.addEventListener('change', () => {
                setTimeout(checkFormCompletion, 100);
            });
        });
    }

    // Setup responsive UI elements
    setupResponsiveUI() {
        // Mobile menu toggle for character panel
        if (window.innerWidth <= 768) {
            this.setupMobileLayout();
        }

        // Listen for window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                this.setupMobileLayout();
            } else {
                this.setupDesktopLayout();
            }
        });
    }

    // Setup mobile layout
    setupMobileLayout() {
        const gameInterface = document.querySelector('.game-interface');
        if (gameInterface) {
            gameInterface.classList.add('mobile-layout');
        }

        // Add mobile menu toggle button
        this.addMobileMenuToggle();
    }

    // Setup desktop layout
    setupDesktopLayout() {
        const gameInterface = document.querySelector('.game-interface');
        if (gameInterface) {
            gameInterface.classList.remove('mobile-layout');
        }

        // Remove mobile menu toggle
        const mobileToggle = document.getElementById('mobile-menu-toggle');
        if (mobileToggle) {
            mobileToggle.remove();
        }
    }

    // Add mobile menu toggle button
    addMobileMenuToggle() {
        if (document.getElementById('mobile-menu-toggle')) return;

        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'mobile-menu-toggle';
        toggleBtn.innerHTML = '☰';
        toggleBtn.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background: rgba(139, 69, 19, 0.9);
            border: 2px solid #d4af37;
            color: #e8d5b7;
            padding: 10px;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
        `;

        toggleBtn.addEventListener('click', () => {
            this.toggleMobileMenu();
        });

        document.body.appendChild(toggleBtn);
    }

    // Toggle mobile menu
    toggleMobileMenu() {
        const characterPanel = document.querySelector('.character-panel');
        const audioPanel = document.querySelector('.audio-panel');
        
        if (characterPanel) {
            characterPanel.style.display = characterPanel.style.display === 'none' ? 'block' : 'none';
        }
        if (audioPanel) {
            audioPanel.style.display = audioPanel.style.display === 'none' ? 'block' : 'none';
        }
    }

    // Show loading indicator
    showLoading(message = 'Loading...') {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'ui-loading';
        loadingDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(44, 24, 16, 0.95);
            color: #e8d5b7;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #d4af37;
            z-index: 9999;
            text-align: center;
            font-family: 'Cinzel', serif;
        `;
        loadingDiv.innerHTML = `
            <div class="loading-spinner" style="
                width: 30px;
                height: 30px;
                border: 3px solid #8b4513;
                border-top: 3px solid #d4af37;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            "></div>
            <p>${message}</p>
        `;
        document.body.appendChild(loadingDiv);
    }

    // Hide loading indicator
    hideLoading() {
        const loadingDiv = document.getElementById('ui-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    // Queue message for display
    queueMessage(message, type = 'info', duration = 3000) {
        this.messageQueue.push({ message, type, duration });
        if (!this.isShowingMessage) {
            this.showNextMessage();
        }
    }

    // Show next message in queue
    showNextMessage() {
        if (this.messageQueue.length === 0) {
            this.isShowingMessage = false;
            return;
        }

        this.isShowingMessage = true;
        const { message, type, duration } = this.messageQueue.shift();
        this.displayMessage(message, type, duration);
    }

    // Display message with styling based on type
    displayMessage(message, type, duration) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `ui-message ui-message-${type}`;
        
        let backgroundColor, borderColor;
        switch (type) {
            case 'error':
                backgroundColor = 'rgba(139, 0, 0, 0.9)';
                borderColor = '#ff0000';
                break;
            case 'success':
                backgroundColor = 'rgba(0, 100, 0, 0.9)';
                borderColor = '#00ff00';
                break;
            case 'warning':
                backgroundColor = 'rgba(139, 69, 0, 0.9)';
                borderColor = '#ff8800';
                break;
            default:
                backgroundColor = 'rgba(139, 69, 19, 0.9)';
                borderColor = '#d4af37';
        }

        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: #e8d5b7;
            padding: 15px 20px;
            border-radius: 8px;
            border: 2px solid ${borderColor};
            z-index: 9999;
            font-family: 'Cinzel', serif;
            max-width: 300px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            animation: slideInRight 0.3s ease-out;
        `;
        messageDiv.textContent = message;
        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                messageDiv.remove();
                this.showNextMessage();
            }, 300);
        }, duration);
    }

    // Create confirmation dialog
    showConfirmation(message, onConfirm, onCancel = null) {
        const confirmDiv = document.createElement('div');
        confirmDiv.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        confirmDiv.innerHTML = `
            <div style="
                background: linear-gradient(135deg, #2c1810, #1a0f0a);
                border: 2px solid #d4af37;
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                color: #e8d5b7;
                font-family: 'Cinzel', serif;
                max-width: 400px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            ">
                <h3 style="margin: 0 0 15px 0; color: #d4af37;">Confirmation</h3>
                <p style="margin: 0 0 20px 0; line-height: 1.5;">${message}</p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button id="confirm-yes" style="
                        background: linear-gradient(45deg, #8b4513, #a0522d);
                        border: 2px solid #d4af37;
                        color: #e8d5b7;
                        padding: 10px 20px;
                        font-family: 'Cinzel', serif;
                        cursor: pointer;
                        border-radius: 6px;
                    ">Yes</button>
                    <button id="confirm-no" style="
                        background: linear-gradient(45deg, #654321, #8b4513);
                        border: 2px solid #8b4513;
                        color: #e8d5b7;
                        padding: 10px 20px;
                        font-family: 'Cinzel', serif;
                        cursor: pointer;
                        border-radius: 6px;
                    ">No</button>
                </div>
            </div>
        `;

        document.body.appendChild(confirmDiv);

        const yesBtn = confirmDiv.querySelector('#confirm-yes');
        const noBtn = confirmDiv.querySelector('#confirm-no');

        yesBtn.addEventListener('click', () => {
            confirmDiv.remove();
            if (onConfirm) onConfirm();
        });

        noBtn.addEventListener('click', () => {
            confirmDiv.remove();
            if (onCancel) onCancel();
        });

        // Close on overlay click
        confirmDiv.addEventListener('click', (e) => {
            if (e.target === confirmDiv) {
                confirmDiv.remove();
                if (onCancel) onCancel();
            }
        });
    }

    // Add CSS animations if not already present
    addAnimations() {
        if (document.getElementById('ui-animations')) return;

        const style = document.createElement('style');
        style.id = 'ui-animations';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }

            .screen-transition {
                animation: fadeIn 0.5s ease-in-out;
            }

            .mobile-layout .character-panel,
            .mobile-layout .audio-panel {
                position: fixed;
                top: 50px;
                left: 10px;
                right: 10px;
                z-index: 999;
                display: none;
            }

            .mobile-layout .main-game-area {
                grid-column: 1 / -1;
            }
        `;
        document.head.appendChild(style);
    }

    // Format numbers with commas
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // Format attribute modifier
    formatModifier(score) {
        const modifier = Math.floor((score - 10) / 2);
        return modifier >= 0 ? `+${modifier}` : `${modifier}`;
    }

    // Truncate text with ellipsis
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    // Create progress bar
    createProgressBar(current, max, width = 100) {
        const percentage = Math.min(100, (current / max) * 100);
        return `
            <div class="progress-bar" style="
                width: ${width}px;
                height: 20px;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #8b4513;
                border-radius: 10px;
                overflow: hidden;
                display: inline-block;
                vertical-align: middle;
            ">
                <div style="
                    width: ${percentage}%;
                    height: 100%;
                    background: linear-gradient(45deg, #228b22, #32cd32);
                    transition: width 0.3s ease;
                "></div>
            </div>
        `;
    }

    // Get element position for tooltips
    getElementPosition(element) {
        const rect = element.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            width: rect.width,
            height: rect.height
        };
    }
}

// Create global UI manager instance
window.uiManager = new UIManager();

// Add CSS animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.uiManager.addAnimations();
});
