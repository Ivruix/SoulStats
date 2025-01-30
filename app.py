import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail
from yandex_cloud_ml_sdk import YCloudML

from db.utils import user_register, user_login, get_usernames, get_user_id, get_user
from ml_backend.agents.chatter import Chatter
from ml_backend.db.utils import create_or_get_today_chat, add_user_message, add_assistant_message, get_chat_by_chat_id

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Настройки для почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'thegoomba4@gmail.com'  # Укажите почту
app.config['MAIL_PASSWORD'] = 'test!'  # Укажите пароль от почты
mail = Mail(app)

PAID_GPT_MESSAGES = 3
MAX_CHAT_LEN = PAID_GPT_MESSAGES * 2 + 1

connection = psycopg2.connect(f"""
    dbname=test
    user=postgres
    password='{os.getenv('DB_PASSWORD')}'
""")

sdk = YCloudML(
    folder_id=os.getenv("FOLDER_ID"),
    auth=os.getenv("YANDEXGPT_API_KEY"),
)

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Все поля должны быть заполнены.", "danger")
            return render_template('login.html')

        username = user_login(connection, username, password)
        user_id = get_user_id(connection, username)

        if username:
            session['username'] = username
            session['user_id'] = user_id
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

        #TODO: Поменять логику с никнеймов на EMAIL!
        usernames_from_db = get_usernames(connection)
        usernames = [user[0] for user in usernames_from_db]

        #TODO: Поменять сообщение с никнейм -> email
        if username in usernames:
            flash("Этот никнейм уже зарегистрирован.", "already_registered")
        else:
            # Заглушка, добавляется в БД только юзернейм!!!
            user_register(connection, username)
            flash("Регистрация успешна! Вы можете войти.", "success")
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

#TODO: Реализовать сброс пароля
        # if email in USERS:
        #     # Отправка письма с ссылкой для сброса пароля
        #     reset_link = url_for('reset_password', _external=True)
        #     msg = Message(
        #         "Восстановление пароля - Умный дневник",
        #         sender='your_email@gmail.com',
        #         recipients=[email]
        #     )
        #     msg.body = f"Здравствуйте!\n\nДля сброса пароля перейдите по ссылке:\n{reset_link}"
        #     mail.send(msg)
        #     flash("Ссылка для восстановления пароля отправлена на ваш email.", "info")
        # else:
        #     flash("Пользователь с таким email не найден.", "danger")
    
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_id = get_user_id(connection, username)
    chat_id = create_or_get_today_chat(connection, user_id)

    return render_template('dashboard.html',
                         chat_id=chat_id,
                         username=username)

@app.route('/send-message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Необходимо войти в систему"})

    data = request.get_json()
    chat_id = data.get('chat_id')
    content = data.get('message')

    if not chat_id or not content:
        return jsonify({"status": "error", "message": "Неверные данные"})

    add_user_message(connection, chat_id, content)

    # Логика ответа нейронки тут
    chat = get_chat_by_chat_id(connection, chat_id)

    chatter_model = sdk.models.completions("yandexgpt").configure(temperature=0.2)
    chatter = Chatter(chatter_model)
    new_message = chatter.generate_response(chat, (MAX_CHAT_LEN - len(chat) + 1) // 2)

    add_assistant_message(connection, chat_id, new_message)

    return jsonify({"status": "success", "reply": new_message})


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Получаем данные пользователя из БД
    user_data = get_user(connection, user_id)

    if not user_data:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('profile.html',
                           user_id=user_data[0],
                           username=user_data[1])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    app.run(debug=True)
