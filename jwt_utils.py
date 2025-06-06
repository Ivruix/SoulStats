import os

import jwt
import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import request, jsonify

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")  # Секретный ключ для подписи токенов
ALGORITHM = "HS256"  # Алгоритм подписи


def create_jwt_token(user_id, username, chat_id=0):
    """Создает JWT токен для пользователя."""
    payload = {
        "user_id": user_id,
        "username": username,
        "chat_id": chat_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Токен действителен 1 час
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_jwt_token(token):
    """Декодирует JWT токен и возвращает данные пользователя."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Токен истёк
    except jwt.InvalidTokenError:
        return None  # Неверный токен


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization") or request.args.get("token")
        if not token:
            return jsonify({"error": "No token"}), 401

        try:
            # Убираем "Bearer " из заголовка (если есть)
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            # Декодируем токен
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            request.user_id = payload["user_id"]
            request.username = payload["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Токен истёк"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Неверный токен"}), 401

        return f(*args, **kwargs)

    return decorated_function
