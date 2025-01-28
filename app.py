from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Настройки для почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'thegoomba4@gmail.com'  # Укажите почту
app.config['MAIL_PASSWORD'] = 'test!'  # Укажите пароль от почты
mail = Mail(app)

# Заглушки данных пользователей
USERS = {
    "admin@example.com": {"username": "admin", "password": "password"},
    "test@test.test": {"username": "Каверин", "password": "1"}
}

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Используем get для безопасности
        password = request.form.get('password')

        if not email or not password:
            flash("Все поля должны быть заполнены.", "danger")
            return render_template('login.html')

        user = USERS.get(email)

        if user and user['password'] == password:
            session['email'] = email
            session['username'] = user['username']
            flash("Вы успешно вошли!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Неверный логин или пароль. Попробуйте снова.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if email in USERS:
            flash("Этот email уже зарегистрирован.", "danger")
        else:
            USERS[email] = {"username": username, "password": password}
            flash("Регистрация успешна! Вы можете войти.", "success")
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        if email in USERS:
            # Отправка письма с ссылкой для сброса пароля
            reset_link = url_for('reset_password', _external=True)
            msg = Message(
                "Восстановление пароля - Умный дневник",
                sender='your_email@gmail.com',
                recipients=[email]
            )
            msg.body = f"Здравствуйте!\n\nДля сброса пароля перейдите по ссылке:\n{reset_link}"
            mail.send(msg)
            flash("Ссылка для восстановления пароля отправлена на ваш email.", "info")
        else:
            flash("Пользователь с таким email не найден.", "danger")
    
    return render_template('forgot_password.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    username = USERS.get(session['email'], {}).get('username', 'Пользователь')
    return render_template('dashboard.html', username=username)

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message', '')

    # Пример простой логики ответа
    if "как дела" in user_message.lower():
        reply = "У меня всё отлично, спасибо, что спросили!"
    elif "куда пепя ляжет" in user_message.lower():
        reply = 'туда сепя сядет...) Конечно интересно, что спросил. Что еще было за сегодня?'
    else:
        reply = "Это интересно! Расскажите подробнее."

    return jsonify({"reply": reply})

@app.route('/logout')
def logout():
    session.clear()
    flash("Вы успешно вышли из системы.", "success")
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    app.run(debug=True)
