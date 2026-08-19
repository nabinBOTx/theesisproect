// Chatbot UI Handler
class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.messageContainer = null;
        this.inputField = null;
        this.sendButton = null;
        this.init();
    }

    init() {
        // Create chatbot HTML if not exists
        if (!document.getElementById('chatbot-widget')) {
            this.createChatbot();
        }
        
        this.messageContainer = document.getElementById('chatbot-messages');
        this.inputField = document.getElementById('chatbot-input');
        this.sendButton = document.getElementById('chatbot-send');
        
        // Attach event listeners
        document.getElementById('chatbot-toggle').addEventListener('click', () => this.toggleChatbot());
        document.getElementById('chatbot-close').addEventListener('click', () => this.closeChatbot());
        document.getElementById('chatbot-reset').addEventListener('click', () => this.resetChat());
        
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Add welcome message
        this.addMessage('assistant', 'Hi! 👋 I\'m your CyberSecure Quest Assistant. I can help explain cybersecurity concepts, answer questions about the games, or provide security tips. What would you like to know?');
    }

    createChatbot() {
        const html = `
            <div id="chatbot-widget" class="chatbot-widget">
                <div class="chatbot-header">
                    <h3>CyberSecure Assistant</h3>
                    <div class="chatbot-controls">
                        <button id="chatbot-reset" title="Reset conversation" class="chatbot-btn-small">↻</button>
                        <button id="chatbot-close" title="Close" class="chatbot-btn-small">×</button>
                    </div>
                </div>
                <div id="chatbot-messages" class="chatbot-messages"></div>
                <div class="chatbot-input-area">
                    <input 
                        type="text" 
                        id="chatbot-input" 
                        placeholder="Ask me about cybersecurity..." 
                        class="chatbot-input"
                    />
                    <button id="chatbot-send" class="chatbot-send-btn">Send</button>
                </div>
            </div>
            <button id="chatbot-toggle" class="chatbot-toggle-btn" title="Open Chat">💬</button>
        `;
        
        document.body.insertAdjacentHTML('beforeend', html);
    }

    toggleChatbot() {
        if (this.isOpen) {
            this.closeChatbot();
        } else {
            this.openChatbot();
        }
    }

    openChatbot() {
        document.getElementById('chatbot-widget').classList.add('open');
        document.getElementById('chatbot-toggle').style.display = 'none';
        this.inputField.focus();
        this.isOpen = true;
    }

    closeChatbot() {
        document.getElementById('chatbot-widget').classList.remove('open');
        document.getElementById('chatbot-toggle').style.display = 'block';
        this.isOpen = false;
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${role}`;
        messageDiv.innerHTML = `<div class="chatbot-message-content">${this.escapeHtml(content)}</div>`;
        this.messageContainer.appendChild(messageDiv);
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // Add user message to UI
        this.addMessage('user', message);
        this.inputField.value = '';
        this.sendButton.disabled = true;

        try {
            // Show loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'chatbot-message assistant loading';
            loadingDiv.innerHTML = '<div class="chatbot-message-content">Thinking...</div>';
            this.messageContainer.appendChild(loadingDiv);
            this.messageContainer.scrollTop = this.messageContainer.scrollHeight;

            // Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove loading indicator
            loadingDiv.remove();

            if (data.error && data.error !== true) {
                this.addMessage('assistant', 'Sorry, I encountered an error: ' + data.error);
            } else if (data.response) {
                this.addMessage('assistant', data.response);
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage('assistant', 'Sorry, I couldn\'t process that. Please try again.');
        } finally {
            this.sendButton.disabled = false;
            this.inputField.focus();
        }
    }

    async resetChat() {
        if (confirm('Clear chat history?')) {
            try {
                await fetch('/api/chat/reset', { method: 'POST' });
                this.messageContainer.innerHTML = '';
                this.addMessage('assistant', 'Chat history cleared! How can I help you now?');
            } catch (error) {
                console.error('Reset error:', error);
                this.addMessage('assistant', 'Error clearing history.');
            }
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatbotWidget();
});
