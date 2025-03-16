import os
from datetime import datetime

import bcrypt
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Mail
from yandex_cloud_ml_sdk import YCloudML

from db.utils import register_user, get_user_id, get_user, get_all_messages, delete_fact
from ml_backend.agents.chatter import Chatter
from ml_backend.chat_db.utils import create_or_get_today_chat, add_user_message, add_assistant_message, get_chat_by_chat_id, \
    analyze_chat, get_facts_by_user
from jwt_utils import create_jwt_token, jwt_required, decode_jwt_token

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Создание папки для голосвых сообщений
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Настройки для почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'thegoomba4@gmail.com'  # Укажите почту
app.config['MAIL_PASSWORD'] = 'test!'  # Укажите пароль от почты
mail = Mail(app)

PAID_GPT_MESSAGES = 4


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

        # TODO: Реализовать сброс пароля
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

    # Получаем данные пользователя из токена
    username = payload['username']
    user_id = payload['user_id']
    chat_id = payload['chat_id']

    # Создаем чат пользователя на сегодня, если его еще нет
    create_or_get_today_chat(connection, user_id)

    # Получаем список чатов пользователя
    cur = connection.cursor()
    cur.execute("SELECT chat_id, created_at FROM chat WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    chats = cur.fetchall()
    cur.close()

    # Форматируем даты для отображения
    chats = [{"chat_id": chat[0], "created_at": chat[1].strftime("%Y-%m-%d")} for chat in chats]

    # Передаем токен, данные и список чатов в шаблон
    return render_template('dashboard.html', chat_id=chat_id, username=username, user_id=user_id, token=token,
                           chats=chats)


@app.route('/get-messages/<int:chat_id>', methods=['GET'])
@jwt_required
def get_messages(chat_id):
    # Получаем сообщения для указанного chat_id
    messages = get_all_messages(connection, chat_id)

    # Форматируем сообщения для ответа
    messages = [{
        "message_id": msg[0],
        "chat_id": msg[1],
        "created_at": msg[2].strftime("%H:%M"),
        "by_user": msg[3],
        "content": msg[4]
    } for msg in messages]

    return jsonify({"status": "success", "messages": messages})


@app.route('/send-message', methods=['POST'])
@jwt_required
def send_message():
    # Получаем данные из запроса
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400
    chat_id = data.get('chat_id')
    content = data.get('message')
    user_id = data.get('user_id')

    # Проверяем, что chat_id и content переданы
    if not chat_id or not content:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    # Добавляем сообщение пользователя в базу данных
    add_user_message(connection, chat_id, content)

    # Получаем чат
    chat = get_chat_by_chat_id(connection, chat_id)

    # Проверяем, что пользователь не превысил лимит сообщений
    if PAID_GPT_MESSAGES <= chat.assistant_message_count():
        return jsonify({"status": "success", "reply": "Вы превысили лимит сообщений на сегодня."})

    # Получаем факты о пользователе
    facts = get_facts_by_user(connection, user_id)
    facts = [fact["content"] for fact in facts]

    # Получаем ответ ассистента
    chatter_model = sdk.models.completions("yandexgpt").configure(temperature=0.2)
    chatter = Chatter(chatter_model)
    new_message = chatter.generate_response(chat, facts, PAID_GPT_MESSAGES - chat.assistant_message_count())

    # Добавляем ответ ассистента в базу данных
    add_assistant_message(connection, chat_id, new_message)

    # Анализируем чат, если это было последнее сообщение ассистента
    if PAID_GPT_MESSAGES - chat.assistant_message_count() == 1:
        analyze_chat(connection, sdk, chat_id, user_id)

    # Возвращаем ответ
    return jsonify({"status": "success", "reply": new_message})


@app.route('/profile')
@jwt_required
def profile():
    # Получаем user_id из JWT токена
    user_id = request.user_id
    # Получаем данные пользователя из базы данных
    user_data = get_user(connection, user_id)

    if not user_data:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for('dashboard'))

    # Распаковываем данные
    user_id, username, created_at = user_data

    # Получаем факты с их fact_id
    facts = get_facts_by_user(connection, user_id)

    # Получаем токен из query-параметра
    token = request.args.get('token')

    # Передаем данные в шаблон
    return render_template('profile.html',
                           user_id=user_id,
                           username=username,
                           facts=facts,
                           token=token)


@app.route('/delete-fact', methods=['POST'])
@jwt_required
def delete_fact_route():
    data = request.get_json()
    if not data or 'fact_id' not in data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    fact_id = data['fact_id']
    user_id = request.user_id

    try:
        cur = connection.cursor()
        cur.execute("SELECT user_id FROM fact WHERE fact_id = %s", (fact_id,))
        fact_user_id = cur.fetchone()
        if not fact_user_id or fact_user_id[0] != user_id:
            return jsonify({"status": "error", "message": "Нет доступа к факту"}), 403

        delete_fact(connection, fact_id)
        connection.commit()
        return jsonify({"status": "success", "message": "Факт удалён"})
    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/create_fact', methods=['POST'])
@jwt_required
def create_fact():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    content = data['content']
    user_id = request.user_id

    try:
        cur = connection.cursor()
        cur.execute("INSERT INTO fact (user_id, content) VALUES (%s, %s) RETURNING fact_id", (user_id, content))
        fact_id = cur.fetchone()[0]
        connection.commit()
        return jsonify({"status": "success", "fact_id": fact_id, "content": content})
    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/update_fact', methods=['POST'])
@jwt_required
def     update_fact():
    data = request.get_json()
    if not data or 'fact_id' not in data or 'content' not in data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    fact_id = data['fact_id']
    content = data['content']
    user_id = request.user_id

    try:
        cur = connection.cursor()
        cur.execute("SELECT user_id FROM fact WHERE fact_id = %s", (fact_id,))
        fact_user_id = cur.fetchone()
        if not fact_user_id or fact_user_id[0] != user_id:
            return jsonify({"status": "error", "message": "Нет доступа к факту"}), 403

        cur.execute("UPDATE fact SET content = %s WHERE fact_id = %s", (content, fact_id))
        connection.commit()
        return jsonify({"status": "success", "message": "Факт обновлён"})
    except Exception as e:
        connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()


@app.route('/stats')
@jwt_required
def stats():
    user_id = request.user_id
    token = request.args.get('token')
    print(f"Rendering stats for user_id: {user_id}, token: {token}")
    return render_template('stats.html', token=token)


@app.route('/get_happiness_data', methods=['GET'])
@jwt_required
def get_happiness_data():
    user_id = request.user_id
    try:
        cur = connection.cursor()
        # Получаем данные из таблицы happiness_level через chat_id
        cur.execute("""
            SELECT c.created_at, hl.val
            FROM happiness_level hl
            JOIN chat c ON hl.chat_id = c.chat_id
            WHERE c.user_id = %s
            ORDER BY c.created_at ASC
        """, (user_id,))
        data = cur.fetchall()
        cur.close()

        print(f"Fetched data: {data}")  # Добавляем отладочный вывод

        # Преобразуем данные для фронтенда
        if not data:
            print("No happiness data found for user_id:", user_id)
            return jsonify({
                'dates': [],
                'levels': [],
                'days_of_week': [],
                'emojis': []
            })

        dates = [row[0].strftime('%Y-%m-%d') for row in data]
        levels = [row[1] for row in data]
        days_of_week = [row[0].strftime('%a') for row in data]  # Получаем сокращённые названия дней (Mon, Tue, ...)

        # Пример маппинга значений happiness_level к эмоциям для смайликов
        emojis = []
        for level in levels:
            if level > 7:
                emojis.append('😊')  # Высокий уровень счастья
            elif level > 4:
                emojis.append('🙂')  # Средний уровень
            else:
                emojis.append('😞')  # Низкий уровень

        return jsonify({
            'dates': dates,
            'levels': levels,
            'days_of_week': days_of_week,
            'emojis': emojis
        })
    except Exception as e:
        print(f"Error in get_happiness_data: {str(e)}")  # Отладочный вывод ошибок
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/upload-voice', methods=['POST'])
@jwt_required
def upload_voice():
    if 'voice' not in request.files:
        return jsonify({"status": "error", "message": "Файл не найден"}), 400

    voice_file = request.files['voice']
    if voice_file.filename == '':
        return jsonify({"status": "error", "message": "Имя файла пустое"}), 400

    user_id = request.user_id

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = voice_file.filename.rsplit('.', 1)
    if len(parts) == 2:
        ext = parts[1]
        new_filename = f"voice_{user_id}_{timestamp}.{ext}"
    else:
        new_filename = f"voice_{user_id}_{timestamp}"

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    voice_file.save(save_path)

    print("Голосовой файл успешно получен:", save_path)

    return jsonify({"status": "success", "message": "Файл успешно получен"})

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
