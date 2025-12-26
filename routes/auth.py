from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
import os
from models.user import User
from database import db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Вход пользователя и возврат JWT токена"""
    try:
        data = request.get_json()
        if not data or not data.get('login') or not data.get('password'):
            return jsonify({'error': 'Missing login or password'}), 400

        login_str = data.get('login')
        password = data.get('password')

        # Поиск пользователя по логину
        user = User.query.filter_by(login=login_str).first()

        if not user:
            return jsonify({'error': 'Invalid login or password'}), 401

        # ✅ УНИВЕРСАЛЬНАЯ проверка пароля (хеш ИЛИ открытый текст)
        password_valid = False

        # Если пароль похож на хеш (длинный) - проверяем через check_password_hash
        if len(user.password) > 50:  # Хеши обычно длиннее 50 символов
            password_valid = check_password_hash(user.password, password)
        else:
            # Старый формат - открытый текст
            password_valid = (user.password == password)

        if not password_valid:
            return jsonify({'error': 'Invalid login or password'}), 401

        # Генерация JWT токена
        token_payload = {
            'user_id': user.user_id,
            'login': user.login,
            'full_name': user.full_name,
            'user_type': user.user_type,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

        return jsonify({
            'access_token': token,
            'user_id': user.user_id,
            'login': user.login,
            'full_name': user.full_name,
            'user_type': user.user_type
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Выход пользователя"""
    try:
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Обновить JWT токен"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Missing token'}), 400

        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        # Получаем обновленную информацию пользователя
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        new_token_payload = {
            'user_id': user.user_id,
            'login': user.login,
            'full_name': user.full_name,
            'user_type': user.user_type,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }

        new_token = jwt.encode(new_token_payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'access_token': new_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
