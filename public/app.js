document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');
    const API_URL = '/api/chat';

    const addMessage = (sender, content) => {
        const messageContainer = document.createElement('div');
        const messageBubble = document.createElement('div');
        messageContainer.classList.add('message-bubble');
        messageBubble.textContent = content;
        messageBubble.classList.add('px-4', 'py-2', 'rounded-lg', 'max-w-xs');
        if (sender === 'user') {
            messageContainer.classList.add('flex', 'justify-end');
            messageBubble.classList.add('bg-indigo-600', 'text-white', 'rounded-br-none');
        } else {
            messageContainer.classList.add('flex', 'justify-start');
            messageBubble.classList.add('bg-gray-700', 'text-white', 'rounded-bl-none');
        }
        messageContainer.appendChild(messageBubble);
        chatWindow.appendChild(messageContainer);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const showTypingIndicator = () => {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.classList.add('flex', 'justify-start', 'message-bubble');
        typingDiv.innerHTML = `<div class="bg-gray-700 text-gray-400 px-4 py-2 rounded-lg max-w-xs rounded-bl-none"><span class="animate-pulse">...</span></div>`;
        chatWindow.appendChild(typingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const removeTypingIndicator = () => {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    };

    messageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;
        addMessage('user', message);
        messageInput.value = '';
        showTypingIndicator();
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });
            if (!response.ok) throw new Error('API request failed');
            const data = await response.json();
            removeTypingIndicator();
            addMessage('bot', data.content);
        } catch (error) {
            removeTypingIndicator();
            addMessage('bot', 'Sorry, I seem to be having some trouble right now.');
            console.error('Error:', error);
        }
    });
});