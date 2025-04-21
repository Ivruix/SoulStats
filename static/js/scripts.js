// Theme Handling
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.remove('dark', 'light');
    document.body.classList.add(savedTheme);

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

    if (savedTheme === 'light') {
        document.querySelectorAll('input, form, button').forEach(el => {
            el.classList.add('light');
        });
    } else {
        document.querySelectorAll('input, form, button').forEach(el => {
            el.classList.remove('light');
        });
    }
}

function toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.contains('light') ? 'light' : 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    body.classList.remove(currentTheme);
    body.classList.add(newTheme);

    document.querySelectorAll('input, form, button').forEach(el => {
        el.classList.remove('light');
        if (newTheme === 'light') el.classList.add('light');
    });

    localStorage.setItem('theme', newTheme);
    const url = new URL(window.location);
    url.searchParams.set('theme', newTheme);
    window.history.pushState({}, '', url);

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

        window.onload = function () {
        const messages = document.getElementById("messages");
        messages.scrollTop = messages.scrollHeight;
    };

    let currentChatId = chatId;

    window.toggleSidebar = function() {
        const sidebar = document.getElementById('sidebar');
        const hamburgerBtn = document.getElementById('hamburger-btn');
        const hamburgerHeadBtn = document.getElementById('hamburger-head-btn');
        sidebar.classList.toggle('hidden');
        hamburgerBtn.textContent = sidebar.classList.contains('hidden') ? '☰' : '✖';
        hamburgerHeadBtn.textContent = sidebar.classList.contains('hidden') ? '☰' : '✖';
    };

function adjustMainPadding() {
    const inputContainer = document.getElementById('input-container');
    const main = document.querySelector('main');
    const sidebarButtons = document.querySelector('.header-buttons');

    if (inputContainer && main) {
        const height = inputContainer.offsetHeight;
        main.style.paddingBottom = `${height + 40}px`;
    }

    if (sidebarButtons) {
        const height = inputContainer.offsetHeight;
        sidebarButtons.style.paddingBottom = `${height + 10}px`;
    }
}

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
                const inputContainer = document.getElementById('input-container');
                const sendButton = document.getElementById('sendButton');
                const messageInput = document.getElementById('messageInput');
                const limitMessage = document.getElementById('limit-message');

                fetch(`/chat-ended/${chatId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem("token")}`
                    }
                })
                .then(response => response.json())
                .then(chatData => {
                    if (chatData.status === 'success' && chatData.ended) {
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
                })
                .catch(error => {
                    console.error('Ошибка при проверке статуса чата:', error);
                });
            }
        })
        .catch(error => {
            console.error('Ошибка при проверке лимита сообщений:', error);
        });
    }

    window.switchChat = function(chatId) {
        currentChatId = chatId;

        if (window.innerWidth < 768) {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.add('hidden');

            const hamburgerBtn = document.getElementById('hamburger-btn');
            const hamburgerHeadBtn = document.getElementById('hamburger-head-btn');
            if (hamburgerBtn) hamburgerBtn.textContent = '☰';
            if (hamburgerHeadBtn) hamburgerHeadBtn.textContent = '☰';

            adjustMainPadding();
        }

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
                const welcomeMessage = document.getElementById('welcome-message');
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

                if (data.messages.length === 0) {
                    welcomeMessage.style.display = 'block';
                } else {
                    welcomeMessage.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при загрузке сообщений');
        });
    };

    window.sendMessage = function() {
        const input = document.getElementById('messageInput');
        const messageText = input.value.trim();
        const welcomeMessage = document.getElementById('welcome-message');

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
        welcomeMessage.style.display = 'none';

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

    window.goToProfile = function() {
        const token = localStorage.getItem("token");
        if (token) {
            window.location.href = `/profile?token=${token}`;
        } else {
            window.location.href = "/login";
        }
    };

    window.handleKeyPress = function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    };

    switchChat(currentChatId);

    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.add('hidden');
    }

    window.addEventListener('resize', () => {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth >= 760) {
        sidebar.classList.remove('hidden');
    } else {
    sidebar.classList.add('hidden');}
    });



    // Вызов при загрузке и изменении размера окна
    window.addEventListener('load', adjustMainPadding);
    window.addEventListener('resize', adjustMainPadding);
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

    window.deleteFact = function(factId) {
        const token = document.body.dataset.token;
        if (!token) {
            alert('Токен отсутствует. Пожалуйста, войдите снова.');
            window.location.href = '/login';
            return;
        }

        if (confirm('Вы уверены, что хотите удалить этот факт?')) {
            fetch('/delete-fact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ fact_id: factId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const factElement = document.querySelector(`[data-fact-id="${factId}"]`);
                    if (factElement) {
                        factElement.remove();
                        alert('Факт успешно удалён.');
                    }
                    const factDivs = document.querySelectorAll('[data-fact-id]');
                    if (factDivs.length === 0) {
                        const factsContainer = document.querySelector('div[style*="Факты:"] > div');
                        factsContainer.innerHTML = '<p style="color: #a0a0c0;">Фактов пока нет.</p>';
                    }
                } else {
                    alert('Ошибка при удалении факта: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении факта.');
            });
        }
    };

    window.editFact = function(factId) {
        const factElement = document.querySelector(`[data-fact-id="${factId}"]`);
        const span = factElement.querySelector('span');
        const originalContent = span.textContent;

        const input = document.createElement('input');
        input.type = 'text';
        input.value = originalContent;
        input.classList.add('fact-input');

        const saveButton = document.createElement('button');
        saveButton.textContent = 'Сохранить';
        saveButton.classList.add('save-btn');
        saveButton.onclick = function() {
            saveFact(factId, input.value);
        };

        const cancelButton = document.createElement('button');
        cancelButton.textContent = 'Отменить';
        cancelButton.classList.add('cancel-btn');
        cancelButton.onclick = function() {
            cancelEdit(factId, originalContent);
        };

        factElement.innerHTML = '';
        factElement.appendChild(input);
        factElement.appendChild(saveButton);
        factElement.appendChild(cancelButton);
    };

    window.saveFact = function(factId, newContent) {
        const token = document.body.dataset.token;
        if (!token) {
            alert('Токен отсутствует. Пожалуйста, войдите снова.');
            window.location.href = '/login';
            return;
        }

        fetch('/update_fact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ fact_id: factId, content: newContent })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const factElement = document.querySelector(`[data-fact-id="${factId}"]`);
                factElement.outerHTML = `
                    <div data-fact-id="${factId}" style="margin: 5px 0; padding: 8px; background: #4a90e2; color: #ffffff; border-radius: 10px; position: relative; display: flex; align-items: center; justify-content: space-between;">
                        <span>${newContent}</span>
                        <div style="display: flex; gap: 0rem;">
                            <button onclick="editFact(${factId})" style="background: none; border: none; color: #ffffff; cursor: pointer; font-size: 1.2rem; padding: 0 8px;">✏️</button>
                            <button onclick="deleteFact(${factId})" style="background: none; border: none; color: #ff4444; cursor: pointer; font-size: 1.2rem; padding: 0 8px;">✖</button>
                        </div>
                    </div>
                `;
                alert('Факт успешно обновлён.');
            } else {
                alert('Ошибка при обновлении факта: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при обновлении факта.');
        });
    };

    window.cancelEdit = function(factId, originalContent) {
        const factElement = document.querySelector(`[data-fact-id="${factId}"]`);
        factElement.outerHTML = `
            <div data-fact-id="${factId}" style="margin: 5px 0; padding: 8px; background: #4a90e2; color: #ffffff; border-radius: 10px; position: relative; display: flex; align-items: center; justify-content: space-between;">
                <span>${originalContent}</span>
                <div style="display: flex; gap: 0rem;">
                    <button onclick="editFact(${factId})" style="background: none; border: none; color: #ffffff; cursor: pointer; font-size: 1.2rem; padding: 0 8px;">✏️</button>
                    <button onclick="deleteFact(${factId})" style="background: none; border: none; color: #ff4444; cursor: pointer; font-size: 1.2rem; padding: 0 8px;">✖</button>
                </div>
            </div>
        `;
    };

    window.goToStats = function() {
        const token = localStorage.getItem("token");
        if (token) {
            window.location.href = `/stats?token=${token}`;
        } else {
            window.location.href = "/login";
        }
    };

    window.addFact = function() {
        const factsContainer = document.getElementById('facts-container');
        const newFactDiv = document.createElement('div');
        newFactDiv.classList.add('new-fact');

        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = 'Введите новый факт';
        input.classList.add('fact-input');

        const saveButton = document.createElement('button');
        saveButton.textContent = 'Сохранить';
        saveButton.classList.add('save-btn');
        saveButton.onclick = function() {
            createFact(input.value, newFactDiv);
        };


        // Добавлена новая кнопка
        const cancelButton = document.createElement('button');
        cancelButton.textContent = 'Отменить';
        cancelButton.classList.add('cancel-btn');
        cancelButton.onclick = function() {
            newFactDiv.remove();
        };

        newFactDiv.appendChild(input);
        newFactDiv.appendChild(saveButton);
        newFactDiv.appendChild(cancelButton);
        factsContainer.appendChild(newFactDiv);
    };

    // Функция для отправки нового факта на сервер
    window.createFact = function(content, newFactDiv) {
        const token = document.body.dataset.token;
        if (!token) {
            alert('Токен отсутствует. Пожалуйста, войдите снова.');
            window.location.href = '/login';
            return;
        }

        fetch('/create_fact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const factId = data.fact_id;
                newFactDiv.outerHTML = `
                    <div data-fact-id="${factId}" style="margin: 5px 0; padding: 8px; background: #4a90e2; color: #ffffff; border-radius: 10px; position: relative; display: flex; align-items: center; justify-content: space-between;">
                        <span>${content}</span>
                        <div style="display: flex; gap: 0rem;">
                            <button onclick="editFact(${factId})" style="background: none; border: none; color: #ffffff; cursor: pointer; font-size: 1.2rem; padding: 0 8px;">✏️</button>
                            <button onclick="deleteFact(${factId})" style="background: none; border: none; color: #ff4444; cursor: pointer; font-size: 1.2rem; padding: 0 8px;">✖</button>
                        </div>
                    </div>
                `;
                alert('Факт успешно добавлен.');
            } else {
                alert('Ошибка при добавлении факта: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при добавлении факта.');
        });
    };

    // Привязка обработчика к кнопке "+"
    document.getElementById('add-fact-btn').addEventListener('click', addFact);
}

function drawHappinessByEmotionChart() {
    const token = localStorage.getItem("token");

    fetch('/get_happiness_by_emotion', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети');
        return response.json();
    })
    .then(data => {
        const colorMap = {
            joy: '#4CAF50',
            sadness: '#2196F3',
            anger: '#F44336',
            anxiety: '#9C27B0',
            disappointment: '#607D8B',
            hope: '#FFC107',
            surprise: '#FF9800',
            neutral: '#9E9E9E',
            unknown: '#616161',
            fear: '#4E3184'
        };

        const emotionNameMap = {
            joy: 'Радость',
            sadness: 'Грусть',
            anger: 'Гнев',
            anxiety: 'Тревога',
            disappointment: 'Разочарование',
            hope: 'Надежда',
            surprise: 'Удивление',
            neutral: 'Нейтрально',
            unknown: 'Неизвестно',
            fear: 'Страх'
        };

        const translatedEmotions = data.emotions.map(
            emotion => emotionNameMap[emotion.toLowerCase()] || emotion
        );

        const trace = {
            x: translatedEmotions,
            y: data.levels,
            type: 'bar',
            marker: {
                color: data.emotions.map(emotion =>
                    colorMap[emotion.toLowerCase()] || '#607D8B'
                )
            },
            text: data.levels.map((_, i) =>
                `Кол-во записей: ${data.counts[i]}`
            ),
            textposition: 'auto',
            hovertemplate:
                'Эмоция: %{x}<br>' +
                'Средний уровень: %{y}<br>' +
                '%{text}<extra></extra>'
        };

        const isLight = document.body.classList.contains('light');

        const layout = {
            title: { text: 'Средний уровень настроения по эмоциям', font: { color: isLight ? '#333' : '#a0a0c0' } },
            xaxis: { title: 'Эмоция', color: isLight ? '#333' : '#a0a0c0'  },
            yaxis: { title: 'Средний уровень настроения', color: isLight ? '#333' : '#a0a0c0'  },
            paper_bgcolor:  isLight ? '#fff' : 'transparent',
            plot_bgcolor:  isLight ? '#fff' : 'transparent'
        };

        const config = {
            staticPlot: true,
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot('happiness-emotion-chart', [trace], layout, config);
    })
    .catch(error => {
        console.error('Ошибка при загрузке данных по эмоциям:', error);
    });
}



function drawEmotionFrequencyChart(period = 'all') {
    const token = localStorage.getItem("token");

    fetch(`/get_emotions_by_period?period=${period}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети');
        return response.json();
    })
    .then(data => {
        const emotionNameMap = {
            joy: 'Радость',
            sadness: 'Грусть',
            anger: 'Гнев',
            anxiety: 'Тревога',
            disappointment: 'Разочарование',
            hope: 'Надежда',
            surprise: 'Удивление',
            neutral: 'Нейтрально',
            unknown: 'Неизвестно',
            fear: 'Страх'
        };

        const translatedEmotions = data.emotions.map(
            emotion => emotionNameMap[emotion.toLowerCase()] || emotion
        );

        // Основной trace: квадратики
        const mainTrace = {
            x: data.weeks,
            y: data.days,
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: window.innerWidth < 480 ? 10 : 18,
                color: data.colors,
                symbol: 'square',
                line: { width: 1, color: '#fff' }
            },
            text: translatedEmotions,
            hovertemplate:
                'Неделя: %{x}<br>' +
                'День: %{y}<br>' +
                'Эмоция: %{text}<extra></extra>',
            showlegend: false
        };

        const legendMap = {};
        for (let i = 0; i < data.emotions.length; i++) {
            const emotion = data.emotions[i];
            const color = data.colors[i];
            if (!(emotion in legendMap)) {
                legendMap[emotion] = color;
            }
        }

        const legendTraces = Object.entries(legendMap).map(([emotion, color]) => ({
            x: [null], y: [null],
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 10,
                color: color,
                symbol: 'square'
            },
            name: emotionNameMap[emotion.toLowerCase()] || emotion,
            showlegend: true,
            hoverinfo: 'none'
        }));

        const isLight = document.body.classList.contains('light');

        const layout = {
            title: { text: 'Частота эмоций по периодам', font: { color: isLight ? '#333' : '#a0a0c0' } },
            xaxis: {
                title: 'Неделя',
                color: isLight ? '#333' : '#a0a0c0',
                dtick: 1,
                showgrid: false
            },
            yaxis: {
                type: 'category',
                categoryorder: 'array',
                categoryarray: ['Пн.', 'Вт.', 'Ср.', 'Чт.', 'Пт.', 'Сб.', 'Вс.'],
                autorange: 'reversed',
               color: isLight ? '#333' : '#a0a0c0',
                showgrid: false
            },
            paper_bgcolor: isLight ? '#fff' : 'transparent',
            plot_bgcolor: isLight ? '#fff' : 'transparent',
            legend: {
                orientation: 'h',
                x: 0,
                y: -0.3,
                font: { color: '#a0a0c0' }
            }
        };

        const config = {
            staticPlot: true,
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot('emotion-period-chart', [mainTrace, ...legendTraces], layout, config);
    })
    .catch(error => {
        console.error('Ошибка при загрузке графика эмоций:', error);
    });
}

function drawHappinessByPeriod(period = 'all') {
    const token = localStorage.getItem("token");

    fetch(`/get_happiness_by_period?period=${period}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети');
        return response.json();
    })
    .then(data => {
        const isLight = document.body.classList.contains('light');

        const trace = {
            x: data.dates,
            y: data.levels,
            mode: 'lines+markers',
            line: { color: isLight ? '#333' : 'white', shape: 'spline' },
            marker: {
                size: 8,
                symbol: 'circle',
                color: data.levels.map(level =>
                    level >= 4 ? '#4CAF50' : level >= 3 ? '#FF9800' : '#F44336'
                )
            },
            text: data.emojis,
            hovertemplate: '%{text}<br>Дата: %{x}<br>Уровень: %{y}<extra></extra>'
        };

        const layout = {
            title: { text: 'Уровень настроения по периодам', font: { color: isLight ? '#333' : '#a0a0c0' } },
            xaxis: { title: 'Период', color: isLight ? '#333' : '#a0a0c0' },
            yaxis: { title: 'Уровень настроения', color: isLight ? '#333' : '#a0a0c0' },
            paper_bgcolor: isLight ? '#ffffff' : 'transparent',
            plot_bgcolor: isLight ? '#ffffff' : 'transparent'
        };

        const config = {
            staticPlot: true,
            displayModeBar: false,
            responsive: true
        };

        Plotly.newPlot('happiness-period-chart', [trace], layout, config);
    })
    .catch(error => {
        console.error('Ошибка при загрузке данных по периодам:', error);
    });
}

// Stats Functions
function initializeStats(token) {
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

    // Функция для построения графиков
    function drawHappinessCharts() {
        const token = localStorage.getItem("token");

        // Запрос данных для графика по периодам
        fetch('/get_happiness_by_period', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.json();
        })
        .then(data => {
            // Линейный график по периодам
            const periodTrace = {
                x: data.dates,
                y: data.levels,
                mode: 'lines+markers',
                line: { color: 'gray' },
                marker: {
                    size: 12,
                    symbol: 'circle',
                    color: data.levels.map(level => level >= 4 ? '#4CAF50' : level >= 3 ? '#FF9800' : '#F44336')
                },
                text: data.emojis,
                hovertemplate: '%{text}<br>Дата: %{x}<br>Уровень: %{y}<extra></extra>'
            };

            const config = {
                staticPlot: true,
                displayModeBar: false,
                responsive: true
            };

            const isLight = document.body.classList.contains('light');

            Plotly.newPlot('happiness-period-chart', [periodTrace], {
                title: { text: 'Уровень настроения по периодам', font: { color: isLight ? '#333' : '#a0a0c0' }  },
                xaxis: { title: 'Период', color: isLight ? '#333' : '#a0a0c0', showgrid: false },
                yaxis: { title: 'Уровень настроения', color: isLight ? '#333' : '#a0a0c0' , showgrid: false },
                paper_bgcolor: isLight ? '#fff' : 'transparent',
                plot_bgcolor: isLight ? '#fff' : 'transparent'
            }, config);
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных по периодам:', error);
        });

        // Запрос данных для графика по дням недели
        fetch('/get_happiness_by_day_of_week', {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.json();
        })
        .then(data => {
            // Столбчатая диаграмма по дням недели
            const dayTrace = {
                x: data.days,
                y: data.levels,
                type: 'bar',
                marker: {
                    color: data.levels.map(level => level >= 4 ? '#4CAF50' : level >= 3 ? '#FF9800' : '#F44336'),
                    line: { width: 1, color: 'rgba(0, 0, 0, 0.1)' }
                },
                text: data.emojis,
                textposition: 'auto',
                hovertemplate: '%{text}<br>День: %{x}<br>Уровень: %{y}<extra></extra>'
            };

            const config = {
                staticPlot: true,
                displayModeBar: false,
                responsive: true
            };

            const isLight = document.body.classList.contains('light');

            Plotly.newPlot('happiness-day-chart', [dayTrace], {
                title: { text: 'Средний уровень настроения по дням недели', font: { color: isLight ? '#333' : '#a0a0c0' }  },
                xaxis: { title: 'День недели', color: isLight ? '#333' : '#a0a0c0' },
                yaxis: { title: 'Уровень настроения', color: isLight ? '#333' : '#a0a0c0' },
                paper_bgcolor: isLight ? '#fff' : 'transparent',
                plot_bgcolor: isLight ? '#fff' : 'transparent'
            }, config);
        })
        .catch(error => {
            console.error('Ошибка при загрузке данных по дням недели:', error);
        });
    }

    // Загружаем Plotly.js и вызываем drawHappinessCharts после загрузки
    const script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
    script.onload = function() {
        console.log('Plotly.js загружен');
        drawHappinessCharts();
        drawHappinessByPeriod();
        drawEmotionFrequencyChart();
        drawHappinessByEmotionChart();
    };
    script.onerror = function() {
        console.error('Ошибка загрузки Plotly.js');
    };
    document.head.appendChild(script);
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

// Recording Voice Functions
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let audioStream;

function toggleRecording() {
    const recordButton = document.getElementById("recordButton");
    const messageInput = document.getElementById("messageInput");

    if (!isRecording) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                audioStream = stream;
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.start();
                isRecording = true;
                recordButton.style.backgroundColor = "red";
                recordButton.textContent = "⏺️ Запись...";

                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener("stop", () => {
                    audioStream.getTracks().forEach(track => track.stop());

                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append("voice", audioBlob, "voice_recording.wav");

                    recordButton.textContent = "⏳ Распознавание...";
                    fetch('/transcribe-voice', {
                        method: 'POST',
                        headers: {
                            "Authorization": `Bearer ${localStorage.getItem("token")}`
                        },
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === "success") {
                            messageInput.value += data.text; // Добавляем текст
                        } else {
                            alert("Ошибка при распознавании голосового сообщения: " + data.message);
                        }
                    })
                    .catch(error => {
                        console.error("Ошибка при распознавании голосового сообщения:", error);
                    })
                    .finally(() => {
                        recordButton.style.backgroundColor = "";
                        recordButton.textContent = "🎤";
                    });
                });
            })
            .catch(error => {
                console.error("Ошибка доступа к микрофону:", error);
                alert("Не удалось получить доступ к микрофону");
            });
    } else {
        mediaRecorder.stop();
        isRecording = false;
        recordButton.style.backgroundColor = "";
        recordButton.textContent = "🎤";
    }
}

// Initialize on Page Load
window.onload = function() {
    initializeTheme();

    const token = document.body.dataset.token;
    const userId = document.body.dataset.userId ? parseInt(document.body.dataset.userId) : null;
    const chatId = document.body.dataset.chatId ? parseInt(document.body.dataset.chatId) : null;

    const currentPath = window.location.pathname;
    if (currentPath === '/dashboard') {
        initializeDashboard(token, userId, chatId);
    } else if (currentPath === '/profile') {
        initializeProfile(token);
    } else if (currentPath === '/stats') {
        initializeStats(token);
    } else if (currentPath === '/login') {
        initializeLogin(token);
    } else if (currentPath === '/register') {
        initializeRegister();
    }

    const hamburgerBtn = document.getElementById('hamburger-btn');
    const hamburgerHeadBtn = document.getElementById('hamburger-head-btn');
    if (hamburgerBtn || hamburgerHeadBtn) {
        hamburgerBtn.addEventListener('click', toggleSidebar);
        hamburgerHeadBtn.addEventListener('click', toggleSidebar);
    }
};

window.addEventListener('resize', () => {
    Plotly.Plots.resize(document.getElementById('emotion-period-chart'));
    Plotly.Plots.resize(document.getElementById('happiness-period-chart'));
    Plotly.Plots.resize(document.getElementById('happiness-day-chart'));
    Plotly.Plots.resize(document.getElementById('happiness-emotion-chart'));
});