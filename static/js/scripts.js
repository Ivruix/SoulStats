// Theme Handling
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.remove('dark', 'light');
    document.body.classList.add(savedTheme);
}

function toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.contains('light') ? 'light' : 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    body.classList.remove(currentTheme);
    body.classList.add(newTheme);
    localStorage.setItem('theme', newTheme);
    const url = new URL(window.location);
    url.searchParams.set('theme', newTheme);
    window.history.pushState({}, '', url);
}

// Dashboard Functions
function initializeDashboard(token, userId, chatId) {
    if (token) {
        localStorage.setItem("token", token);
    }

    let currentChatId = chatId;

    // Switch Chat
    window.switchChat = function(chatId) {
        currentChatId = chatId;

        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.getAttribute('onclick').match(/\d+/)[0]) === chatId) {
                item.classList.add('active');
            }
        });

        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = '';

        fetch(`/get-messages/${chatId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem("token")}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                data.messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.classList.add('message', msg.by_user ? 'user' : 'assistant');
                    messageDiv.innerHTML = `
                        <p>${msg.content}</p>
                        <div class="message-time">${msg.created_at}</div>
                    `;
                    messagesDiv.appendChild(messageDiv);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при загрузке сообщений');
        });
    };

    // Send Message
    window.sendMessage = function() {
        const input = document.getElementById('messageInput');
        const messageText = input.value.trim();

        if (messageText === '') return;

        const messagesDiv = document.getElementById('messages');
        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user');
        userMessage.innerHTML = `
            <p>${messageText}</p>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        messagesDiv.appendChild(userMessage);
        input.value = '';

        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        fetch('/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify({
                chat_id: currentChatId,
                message: messageText,
                user_id: userId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                const assistantMessage = document.createElement('div');
                assistantMessage.classList.add('message', 'assistant');
                assistantMessage.innerHTML = `
                    <p>${data.reply}</p>
                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                `;
                messagesDiv.appendChild(assistantMessage);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при отправке сообщения');
        });
    };

    // Go to Profile
    window.goToProfile = function() {
        const token = localStorage.getItem("token");
        if (token) {
            window.location.href = `/profile?token=${token}`;
        } else {
            window.location.href = "/login";
        }
    };

    // Handle Key Press
    window.handleKeyPress = function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    };

    // Initialize the chat
    switchChat(currentChatId);
}

// Profile Functions
function initializeProfile(token) {
    if (token) {
        localStorage.setItem("token", token);
    }

    window.goToDashboard = function() {
        const token = localStorage.getItem("token");
        if (token) {
            window.location.href = `/dashboard?token=${token}`;
        } else {
            window.location.href = "/login";
        }
    };
}

// Login Functions
function initializeLogin(token) {
    if (token) {
        localStorage.setItem("token", token);
    }

    fetch("/dashboard", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
}

// Register Functions
function initializeRegister() {
    fetch("/dashboard", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });
}

// Initialize on Page Load
window.onload = function() {
    initializeTheme();

    // Check if the page has specific data attributes and initialize accordingly
    const token = document.body.dataset.token;
    const userId = document.body.dataset.userId ? parseInt(document.body.dataset.userId) : null;
    const chatId = document.body.dataset.chatId ? parseInt(document.body.dataset.chatId) : null;

    if (document.body.classList.contains('dashboard-page')) {
        initializeDashboard(token, userId, chatId);
    } else if (document.body.classList.contains('profile-page')) {
        initializeProfile(token);
    } else if (document.body.classList.contains('login-page')) {
        initializeLogin(token);
    } else if (document.body.classList.contains('register-page')) {
        initializeRegister();
    }
};