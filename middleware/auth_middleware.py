# middleware/auth_middleware.py

from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService

def require_auth(f):
    """
    Декоратор для проверки наличия валидного токена

    Использование:
    @require_auth
    def protected_route():
        ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Получение токена из header
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Missing Authorization header'}), 401

        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid Authorization header format'}), 401

        token = auth_header.split(' ')[1]

        # Проверка токена
        payload, error = AuthService.verify_token(token)

        if error:
            return jsonify({'error': error}), 401

        # Передача данных пользователя в функцию
        kwargs['current_user'] = payload
        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    Декоратор для проверки роли пользователя

    Использование:
    @require_role('Менеджер', 'Специалист')
    def admin_route(current_user):
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Получение токена
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid Authorization header'}), 401

            token = auth_header.split(' ')[1]

            # Проверка токена
            payload, error = AuthService.verify_token(token)

            if error:
                return jsonify({'error': error}), 401

            # Проверка роли
            user_type = payload.get('user_type')

            if user_type not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_role': allowed_roles,
                    'user_role': user_type
                }), 403

            # Передача данных в функцию
            kwargs['current_user'] = payload
            return f(*args, **kwargs)

        return decorated_function

    return decorator
