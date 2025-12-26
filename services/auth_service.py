# services/auth_service.py

import jwt
import datetime
from models.user import User
from database import db
from config import Config
from werkzeug.security import check_password_hash


class AuthService:
    SECRET_KEY = 'your-secret-key-change-in-production'
    ALGORITHM = 'HS256'

    @staticmethod
    def login_user(login: str, password: str):
        try:
            user = User.query.filter_by(login=login).first()

            if not user:
                return {'error': 'Invalid login or password'}, 401

            # === DEBUG OUTPUT ===
            print("\n" + "=" * 70)
            print(f"LOGIN ATTEMPT: {login}")
            print(f"Password from DB (first 40 chars): {user.password[:40]}")
            print(f"Password from DB length: {len(user.password)}")
            print(f"Entered password: '{password}'")
            print(f"Entered password length: {len(password)}")
            print("=" * 70)

            password_valid = False

            # Check hashed password
            if len(user.password) > 20:
                try:
                    result = check_password_hash(user.password, password)
                    print(f"check_password_hash result: {result}")
                    if result:
                        password_valid = True
                        print("SUCCESS: Hash check passed!")
                    else:
                        print("FAIL: Hash check failed!")
                except Exception as e:
                    print(f"ERROR in check_password_hash: {e}")

            # Check plain text
            if not password_valid:
                if user.password == password:
                    password_valid = True
                    print("SUCCESS: Plain text match!")
                else:
                    print("FAIL: Plain text mismatch!")

            if not password_valid:
                print("AUTHENTICATION FAILED!")
                print("=" * 70 + "\n")
                return {'error': 'Invalid login or password'}, 401

            print("AUTHENTICATION SUCCESS!")
            print("=" * 70 + "\n")

            token = AuthService.generate_token(user)

            return {
                'access_token': token,
                'user_id': user.user_id,
                'full_name': user.full_name,
                'login': user.login,
                'user_type': user.user_type,
                'phone': user.phone,
                'message': 'Login successful'
            }, 200

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500

    @staticmethod
    def generate_token(user):
        payload = {
            'user_id': user.user_id,
            'login': user.login,
            'user_type': user.user_type,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, AuthService.SECRET_KEY, algorithm=AuthService.ALGORITHM)

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=[AuthService.ALGORITHM])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token expired'
        except jwt.InvalidTokenError:
            return None, 'Invalid token'

    @staticmethod
    def get_current_user(token: str):
        payload, error = AuthService.verify_token(token)
        if error:
            return None, error
        user = User.query.get(payload['user_id'])
        if not user:
            return None, 'User not found'
        return user, None
