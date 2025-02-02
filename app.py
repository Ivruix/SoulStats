import os

import bcrypt
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail
from yandex_cloud_ml_sdk import YCloudML

from db.utils import register_user, user_login, get_usernames, get_user_id, get_user
from ml_backend.agents.chatter import Chatter
from ml_backend.db.utils import create_or_get_today_chat, add_user_message, add_assistant_message, get_chat_by_chat_id
from jwt_utils import create_jwt_token, jwt_required, decode_jwt_token

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

        # Получаем пользователя из базы данных
        user_id = get_user_id(connection, username)
        user = get_user(connection, user_id)

        if not user:
            flash("Неверный логин или пароль.", "danger")
            return render_template('login.html')

        user_id, db_username, password_hash = user

        # Проверяем пароль
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            flash("Неверный логин или пароль.", "danger")
            return render_template('login.html')

        # Создаём чат с пользователем
        chat_id = create_or_get_today_chat(connection, user_id)

        # Создаем JWT токен
        token = create_jwt_token(user_id, db_username, chat_id)

        # Перенаправляем на dashboard с токеном
        return redirect(url_for('dashboard', token=token))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Проверяем, что все поля заполнены
        if not email or not username or not password:
            flash("Все поля должны быть заполнены.", "danger")
            return render_template('register.html')

        # Проверяем, что пользователь с таким email или username не существует
        cur = connection.cursor()
        cur.execute("SELECT * FROM user_data WHERE email = %s OR username = %s", (email, username))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            flash("Пользователь с таким email или именем уже зарегистрирован.", "danger")
            return render_template('register.html')

        # Хэшируем пароль
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Сохраняем пользователя в базу данных
        register_user(connection, username, email, password_hash)

        # Сразу же получаем ID нового пользователя
        user_id = get_user_id(connection, username)

        # Создаём токен
        token = create_jwt_token(user_id, username)

        # Возвращаем токен пользователю
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
    # Получаем токен из query-параметра (если он есть)
    token = request.args.get('token')

    if not token:
        # Если токен не передан, проверяем его в куках или localStorage (на фронтенде)
        return redirect(url_for('login'))

    # Декодируем токен
    payload = decode_jwt_token(token)
    if not payload:
        flash("Неверный или истёкший токен. Пожалуйста, войдите снова.", "danger")
        return redirect(url_for('login'))
    print(payload)

    # Получаем данные пользователя из токена
    username = payload['username']
    user_id = payload['user_id']
    chat_id = payload['chat_id']

    # Передаем токен и данные в шаблон
    return render_template('dashboard.html', chat_id=chat_id, username=username, token=token)

@app.route('/send-message', methods=['POST'])
@jwt_required  # Проверяем JWT токен
def send_message():
    # Получаем данные из запроса
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    chat_id = data.get('chat_id')
    content = data.get('message')

    # Проверяем, что chat_id и content переданы
    if not chat_id or not content:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    # Добавляем сообщение пользователя в базу данных
    add_user_message(connection, chat_id, content)

    # Логика ответа нейронки
    chat = get_chat_by_chat_id(connection, chat_id)

    chatter_model = sdk.models.completions("yandexgpt").configure(temperature=0.2)
    chatter = Chatter(chatter_model)
    new_message = chatter.generate_response(chat, (MAX_CHAT_LEN - len(chat) + 1) // 2)

    # Добавляем ответ ассистента в базу данных
    add_assistant_message(connection, chat_id, new_message)

    # Возвращаем ответ
    return jsonify({"status": "success", "reply": new_message})

@app.route('/profile')
@jwt_required  # Проверяем JWT токен
def profile():
    # Получаем user_id из JWT токена
    print(1)
    user_id = request.user_id

    # Получаем данные пользователя из базы данных
    user_data = get_user(connection, user_id)

    if not user_data:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for('dashboard'))

    # Распаковываем данные
    user_id, username, created_at = user_data

    # Передаем данные в шаблон
    return render_template('profile.html',
                         user_id=user_id,
                         username=username,
                         registration_date=created_at)

@app.route('/logout')
def logout():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Выход</title>
        <script>
            localStorage.removeItem("token");
            window.location.href = "/";
        </script>
    </head>
    <body>
        <p>Выполняется выход...</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
