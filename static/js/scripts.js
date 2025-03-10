// Theme Handling
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.remove('dark', 'light');
    document.body.classList.add(savedTheme);

    // Update theme icon on page load
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        if (savedTheme === 'light') {
            themeIcon.innerHTML = `
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4z"/>
            `;
        } else {
            themeIcon.innerHTML = `
                <path fill-rule="nonzero" d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.414-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/>
             `;
        }
    }
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

    // Update theme icon
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        if (newTheme === 'light') {
            themeIcon.innerHTML = `
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4z"/>
            `;
        } else {
            themeIcon.innerHTML = `
                <path fill-rule="nonzero" d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.414-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/>
             `;
        }
    }
}

// Dashboard Functions
function initializeDashboard(token, userId, chatId) {
    if (token) {
        localStorage.setItem("token", token);
    }

    const MESSAGE_LIMIT = 7;
    let currentChatId = chatId;

    // Function to toggle sidebar visibility
    window.toggleSidebar = function() {
        const sidebar = document.getElementById('sidebar');
        const hamburgerBtn = document.getElementById('hamburger-btn');
        const hamburgerHeadBtn = document.getElementById('hamburger-head-btn');
        sidebar.classList.toggle('hidden');
        hamburgerBtn.textContent = sidebar.classList.contains('hidden') ? '☰' : '✖';
        hamburgerHeadBtn.textContent = sidebar.classList.contains('hidden') ? '☰' : '✖';
    };

    function checkMessageLimit(chatId) {
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
                const messageCount = data.messages.length;
                const inputContainer = document.getElementById('input-container');
                const sendButton = document.getElementById('sendButton');
                const messageInput = document.getElementById('messageInput');
                const limitMessage = document.getElementById('limit-message');

                if (messageCount >= MESSAGE_LIMIT) {
                    inputContainer.classList.add('disabled');
                    sendButton.disabled = true;
                    messageInput.disabled = true;
                    limitMessage.style.display = 'block';
                } else {
                    inputContainer.classList.remove('disabled');
                    sendButton.disabled = false;
                    messageInput.disabled = false;
                    limitMessage.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при проверке лимита сообщений:', error);
        });
    }

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
                checkMessageLimit(chatId);
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
                checkMessageLimit(currentChatId);
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

    // Ensure sidebar is hidden on mobile by default
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.add('hidden');
    }
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

    const hamburgerBtn = document.getElementById('hamburger-btn');
    const hamburgerHeadBtn = document.getElementById('hamburger-head-btn')
    if (hamburgerBtn || hamburgerHeadBtn) {
        hamburgerBtn.addEventListener('click', toggleSidebar);
        hamburgerHeadBtn.addEventListener('click', toggleSidebar);

    }
};