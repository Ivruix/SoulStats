import os
import datetime
from urllib.parse import quote

import bcrypt
import jwt

from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, render_template_string
from flask_mail import Mail
from flask_mail import Message as FlaskMessage

from jwt_utils import create_jwt_token, jwt_required, decode_jwt_token

from ml_backend.utils import analyze_chat, get_next_question, should_extend_chat
from ml_backend.speech_recognition.whisper_singleton import WhisperRecognizer

from db.user_data import UserData
from db.message import Message
from db.fact import Fact
from db.chat import Chat
from db.stats import Stats

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Создание папки для голосовых сообщений
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Получение ключа для почты и саму почту
MAIL_PASS = os.getenv("MAIL_PASSWORD")
MAIL = os.getenv("MAIL_USERNAME")

# Настройки для почты
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL
app.config['MAIL_PASSWORD'] = MAIL_PASS
app.config['MAIL_DEFAULT_SENDER'] = MAIL
mail = Mail(app)

MAX_PAID_GPT_MESSAGES = 10


@app.route('/test_email')
def test_email():
    from flask_mail import Message
    msg = Message("Привет от SoulStats!", recipients=["kav.max007@gmail.com"])
    msg.body = "Это тестовое письмо. Всё настроено правильно :)"
    mail.send(msg)
    return "Письмо отправлено!"


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
        user_id = UserData.get_user_id(username)
        user = UserData.get_user(user_id)

        if not user:
            flash("Неверный логин или пароль.", "danger")
            return render_template('login.html')

        user_id, db_username, password_hash = user

        # Проверяем пароль
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            flash("Неверный логин или пароль.", "danger")
            return render_template('login.html')

        # Создаём чат с пользователем
        chat_id = Chat.create_or_get_today_chat(user_id)

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
        if UserData.already_in_use(email, username):
            flash("Пользователь с таким email или именем уже зарегистрирован.", "danger")
            return render_template('register.html')

        # Хэшируем пароль
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Сохраняем пользователя в базу данных
        UserData.register_user(username, email, password_hash)

        # Сразу же получаем ID нового пользователя
        user_id = UserData.get_user_id(username)

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

        user = UserData.get_user_by_email(email)

        if not user:
            email = '$unsub_' + email
            user = UserData.get_user_by_email(email)

        if user:
            user_id, username = user
            send_reset_password_email(user_id, username, email)
            flash("Ссылка для восстановления пароля отправлена на ваш email.", "info")
        else:
            flash("Пользователь с таким email не найден.", "danger")

    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return "Срок действия ссылки истёк"
    except jwt.InvalidTokenError:
        return "Недействительная ссылка"

    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Пароли не совпадают.", "danger")
            return render_template('reset_password.html', token=token)

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        UserData.update_password(user_id, hashed)
        flash("Пароль успешно обновлён. Войдите с новым паролем.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


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
    Chat.create_or_get_today_chat(user_id)

    # Получаем список чатов пользователя
    chats = Chat.get_chats_by_user(user_id)

    # Форматируем даты для отображения
    chats = [{"chat_id": chat[0], "created_at": chat[1].strftime("%Y-%m-%d")} for chat in chats]

    # Передаем токен, данные и список чатов в шаблон
    return render_template('dashboard.html', chat_id=chat_id, username=username, user_id=user_id, token=token,
                           chats=chats)


@app.route('/get-messages/<int:chat_id>', methods=['GET'])
@jwt_required
def get_messages(chat_id):
    # Получаем сообщения для указанного chat_id
    messages = Message.get_all_messages(chat_id)

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

    # Проверяем, что пользователь не превысил лимит сообщений
    if Chat.get_chat_by_chat_id(chat_id).assistant_message_count() >= MAX_PAID_GPT_MESSAGES:
        return jsonify({"status": "success", "reply": "Вы превысили лимит сообщений на сегодня."})

    # Проверяем, завершен ли чат
    if Chat.has_ended(chat_id):
        return jsonify({"status": "success", "reply": "Чат завершен."})

    # Добавляем сообщение пользователя в базу данных
    Message.add_user_message(chat_id, content)

    # Получаем чат
    chat = Chat.get_chat_by_chat_id(chat_id)

    # Получаем факты о пользователе
    facts = Fact.get_facts_by_user(user_id)
    facts = [fact["content"] for fact in facts]

    # Получаем ответ ассистента
    last_message = MAX_PAID_GPT_MESSAGES - chat.assistant_message_count() == 1 or not should_extend_chat(chat)
    new_message = get_next_question(chat, facts, last_message)

    # Добавляем ответ ассистента в базу данных
    Message.add_assistant_message(chat_id, new_message)

    # Проверяем, сработал ли фильтр
    if new_message == "Давайте завершим этот диалог.":
        last_message = True

    # Если чат завершен, анализируем его и помечаем как завершенный
    if last_message:
        analyze_chat(chat_id, user_id)
        Chat.mark_chat_as_ended(chat_id)

    # Возвращаем ответ
    return jsonify({"status": "success", "reply": new_message})


@app.route('/chat-ended/<int:chat_id>', methods=['GET'])
@jwt_required
def chat_ended(chat_id):
    ended = Chat.has_ended(chat_id)
    return jsonify({"status": "success", "ended": ended})


@app.route('/profile')
@jwt_required
def profile():
    # Получаем user_id из JWT токена
    user_id = request.user_id
    # Получаем данные пользователя из базы данных
    user_data = UserData.get_user(user_id)

    if not user_data:
        flash("Пользователь не найден.", "danger")
        return redirect(url_for('dashboard'))

    # Распаковываем данные
    user_id, username, created_at = user_data

    # Получаем факты с их fact_id
    facts = Fact.get_facts_by_user(user_id)

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
        fact_user_id = Fact.get_user_id_by_fact_id(fact_id)
        if not fact_user_id or fact_user_id != user_id:
            return jsonify({"status": "error", "message": "Нет доступа к факту"}), 403

        Fact.delete_fact(fact_id)
        return jsonify({"status": "success", "message": "Факт удалён"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/create_fact', methods=['POST'])
@jwt_required
def create_fact():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    content = data['content']
    user_id = request.user_id

    try:
        fact_id = Fact.create_fact(user_id, content)
        return jsonify({"status": "success", "fact_id": fact_id, "content": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/update_fact', methods=['POST'])
@jwt_required
def update_fact():
    data = request.get_json()
    if not data or 'fact_id' not in data or 'content' not in data:
        return jsonify({"status": "error", "message": "Неверные данные"}), 400

    fact_id = data['fact_id']
    content = data['content']
    user_id = request.user_id

    try:
        fact_user_id = Fact.get_user_id_by_fact_id(fact_id)
        if not fact_user_id or fact_user_id != user_id:
            return jsonify({"status": "error", "message": "Нет доступа к факту"}), 403

        Fact.update_fact(fact_id, content)
        return jsonify({"status": "success", "message": "Факт обновлён"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/stats')
@jwt_required
def stats():
    user_id = request.user_id
    token = request.args.get('token')
    print(f"Rendering stats for user_id: {user_id}, token: {token}")
    return render_template('stats.html', token=token)


@app.route('/get_happiness_by_period', methods=['GET'])
@jwt_required
def get_happiness_by_period():
    user_id = request.user_id
    period = request.args.get('period', 'all')  # 'week', 'month' или 'all'
    try:
        data = Stats.get_happiness_by_period(user_id, period)
        if not data:
            return jsonify({
                'dates': [],
                'levels': [],
                'emojis': []
            })

        dates = [row[0].strftime('%Y-%m-%d') for row in data]
        levels = [row[1] for row in data]

        # Эмодзи в зависимости от уровня счастья
        emoji_map = {
            5: "😄",
            4: "🙂",
            3: "😐",
            2: "😔",
            1: "😢"
        }
        emojis = [emoji_map.get(level, "😐") for level in levels]

        return jsonify({
            'dates': dates,
            'levels': levels,
            'emojis': emojis
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_happiness_by_day_of_week', methods=['GET'])
@jwt_required
def get_happiness_by_day_of_week():
    user_id = request.user_id
    try:
        data = Stats.get_average_happiness_by_day_of_week(user_id)
        if not data:
            return jsonify({
                'days': [],
                'levels': [],
                'emojis': []
            })

        days = [row[0] for row in data]  # День недели
        levels = [row[1] for row in data]  # Средний уровень счастья
        days_map = {
            "Monday": "Пн.",
            "Tuesday": "Вт.",
            "Wednesday": "Ср.",
            "Thursday": "Чт.",
            "Friday": "Пт.",
            "Saturday": "Сб.",
            "Sunday": "Вс."
        }
        days = [days_map.get(day.strip(), day.strip()) for day in days]  # Переводим дни недели на русский

        emojis = []
        for level in levels:
            if level >= 4.5:
                emojis.append("😄")
            elif level >= 3.5:
                emojis.append("🙂")
            elif level >= 2.5:
                emojis.append("😐")
            elif level >= 1.5:
                emojis.append("😔")
            else:
                emojis.append("😢")

        return jsonify({
            'days': days,
            'levels': levels,
            'emojis': emojis
        })
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_happiness_by_emotion', methods=['GET'])
@jwt_required
def get_happiness_by_emotion():
    user_id = request.user_id
    try:
        data = Stats.get_average_happiness_by_emotion(user_id)
        if not data:
            return jsonify({
                'emotions': [],
                'levels': [],
                'counts': []
            })

        emotions = [row[0] for row in data]
        levels = [row[1] for row in data]  # Средний уровень счастья
        counts = [row[2] for row in data]  # Количество записей для каждой эмоции

        return jsonify({
            'emotions': emotions,
            'levels': levels,
            'counts': counts
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_emotions_by_period', methods=['GET'])
@jwt_required
def get_emotions_by_period():
    user_id = request.user_id
    period = request.args.get('period', 'all')  # 'week', 'month' или 'all'
    try:
        data = Stats.get_emotions_by_period(user_id, period)
        if not data:
            return jsonify({
                'dates': [],
                'weeks': [],
                'days': [],
                'emotions': [],
                'colors': []
            })

        dates = [row[0].strftime('%Y-%m-%d') for row in data]
        weeks = []
        days = []
        emotions = []
        colors = []

        day_map = {
            0: 'Пн.',
            1: 'Вт.',
            2: 'Ср.',
            3: 'Чт.',
            4: 'Пт.',
            5: 'Сб.',
            6: 'Вс.'
        }

        color_map = {
            'joy': '#4CAF50',  # green
            'sadness': '#2196F3',  # blue
            'anger': '#F44336',  # red
            'anxiety': '#9C27B0',  # purple
            'disappointment': '#607D8B',  # blue-gray
            'hope': '#FFC107',  # yellow
            'surprise': '#FF9800',  # orange
            'fear': '#844D9E',  # purple
            'neutral': '#9E9E9E',  # gray
            'unknown': '#616161',  # dark gray
        }

        for created_at, emotion in data:
            week_number = created_at.isocalendar()[1]
            weekday_number = created_at.weekday()  # Понедельник = 0
            day_name = day_map.get(weekday_number, str(weekday_number))

            weeks.append(week_number)
            days.append(day_name)
            emotions.append(emotion)
            colors.append(color_map.get(emotion.lower(), '#607D8B'))

        return jsonify({
            'dates': dates,
            'weeks': weeks,
            'days': days,
            'emotions': emotions,
            'colors': colors
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/transcribe-voice', methods=['POST'])
@jwt_required
def transcribe_voice():
    if 'voice' not in request.files:
        return jsonify({"status": "error", "message": "Файл не найден"}), 400

    voice_file = request.files['voice']
    if voice_file.filename == '':
        return jsonify({"status": "error", "message": "Имя файла пустое"}), 400

    user_id = request.user_id

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = voice_file.filename.rsplit('.', 1)
    if len(parts) == 2:
        ext = parts[1]
        new_filename = f"voice_{user_id}_{timestamp}.{ext}"
    else:
        new_filename = f"voice_{user_id}_{timestamp}"

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    voice_file.save(save_path)

    recognizer = WhisperRecognizer()
    transcribed_text = recognizer.transcribe(save_path)

    return jsonify({"status": "success", "message": "Файл успешно распознан", "text": transcribed_text})


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

def generate_unsubscribe_token(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload, app.secret_key, algorithm="HS256")
    return token

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    token = request.args.get('token')
    if not token:
        return "Неверный запрос", 400

    try:
        payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        email = payload["email"]
        UserData.unsubscribe_user(email)
        return "Вы успешно отписались от уведомлений."
    except jwt.ExpiredSignatureError:
        return "Токен истёк", 400
    except jwt.InvalidTokenError:
        return "Неверный токен", 400

def end_old_chats():
    print("Ending old chats...")
    current_date = datetime.date.today()
    active_chats = Chat.get_active_chats()
    ended = 0
    for chat_id, user_id, created_at in active_chats:
        if created_at < current_date:
            ended += 1
            analyze_chat(chat_id, user_id)
            Chat.mark_chat_as_ended(chat_id)
    print(f"Ended {ended} old chats.")


def send_reminder_email(user_id, username, email):
    with app.app_context():
        link = f"https://soulstats.ru/dashboard?token={create_jwt_token(user_id, username)}"
        unsubscribe_token = generate_unsubscribe_token(email)
        unsubscribe_url = f"https://soulstats.ru/unsubscribe?token={unsubscribe_token}"

        with open("templates/email_reminder_template.html", encoding="utf-8") as template_file:
            template = template_file.read()

        html_body = render_template_string(template, username=username, url=link, unsubscribe_url=unsubscribe_url)
        msg = FlaskMessage(subject="Обновление в SoulStats 💬", recipients=[email])
        msg.html = html_body
        mail.send(msg)


def send_reset_password_email(user_id, username, email):
    with app.app_context():
        token = create_jwt_token(user_id, username)

        reset_link = url_for('reset_password', token=token, _external=True)

        with open("templates/password_reset_email.html", encoding="utf-8") as template_file:
            template = template_file.read()

        html_body = render_template_string(template, username=username, url=reset_link)

        if '$unsub_' in email:
            email = email.replace('$unsub_', '')

        msg = FlaskMessage(subject="Восстановление пароля — SoulStats", recipients=[email])
        msg.html = html_body
        mail.send(msg)


def remind_users():
    users = UserData.get_all_users()
    for user_id, username, email in users:
        if '$unsub_' in email:
            continue
        latest = Chat.get_latest_chat(user_id)

        if not latest or latest[1] != datetime.date.today():
            send_reminder_email(user_id, username, email)


# Запуск фонового планировщика (для тестового использования)
def start_test_scheduler():
    end_old_chats()

    scheduler = BackgroundScheduler()
    scheduler.add_job(end_old_chats, 'interval', hours=1)
    scheduler.start()


# Запуск блокирующего планировщика (для продакшн использования)
def start_production_scheduler():
    end_old_chats()

    scheduler = BlockingScheduler()
    scheduler.add_job(remind_users, 'cron', hour=20, minute=00)
    scheduler.add_job(end_old_chats, 'interval', hours=1)
    scheduler.start()


if __name__ == '__main__':
    start_test_scheduler()
    app.run(debug=True)
