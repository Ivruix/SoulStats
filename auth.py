from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
import jwt
import psycopg2
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

# Конфигурация
SECRET_KEY = os.getenv('JWT_SECRET')
DB_CONFIG = {
    'dbname': 'your_db',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost'
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@auth_bp.post('/register')
def register_user():
    data = request.get_json()

    # Валидация входных данных
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    username = data['username']
    email = data['email']
    password = data['password']

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Проверка существующего пользователя
        cur.execute(
            "SELECT * FROM user_data WHERE username = %s OR email = %s",
            (username, email)
        )
        if cur.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 409

        # Хеширование пароля
        hashed_password = generate_password_hash(password)

        # Создание пользователя
        cur.execute(
            "INSERT INTO user_data (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, hashed_password)
        )
        user_id = cur.fetchone()[0]
        conn.commit()

        # Генерация JWT токена
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.now() + timedelta(days=30)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': user_id
        }), 201

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()
