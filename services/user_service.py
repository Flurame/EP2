from database import db
from werkzeug.security import generate_password_hash


class UserService:
    @staticmethod
    def get_all_users():
        try:
            from models.user import User
            users = User.query.all()
            return [u.to_dict() for u in users]
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_user_by_id(user_id):
        try:
            from models.user import User
            user = User.query.get(user_id)
            if not user:
                return None
            return user.to_dict()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_specialists():
        try:
            from models.user import User
            specialists = User.query.filter_by(user_type="Специалист").all()
            return [u.to_dict() for u in specialists]
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def list_assignable_users():
        """
        Пользователи, которых можно назначать ответственными.
        Если захочешь — можно ограничить по ролям.
        """
        try:
            from models.user import User
            users = User.query.order_by(User.full_name).all()
            return users
        except Exception as e:
            # ВАЖНО: здесь возвращаем пустой список, чтобы фронт не падал
            return []

    @staticmethod
    def create_user(full_name, phone, login, password, user_type="Заказчик"):
        try:
            from models.user import User

            existing_user = User.query.filter_by(login=login).first()
            if existing_user:
                return {"error": "User with this login already exists"}

            if not full_name or not full_name.strip():
                return {"error": "Full name cannot be empty"}
            if not phone or not phone.strip():
                return {"error": "Phone cannot be empty"}
            if not login or not login.strip():
                return {"error": "Login cannot be empty"}
            if not password or not password.strip():
                return {"error": "Password cannot be empty"}

            full_name = full_name.strip()
            phone = phone.strip()
            login = login.strip()
            password = password.strip()

            if len(login) < 3:
                return {"error": "Login must be at least 3 characters long"}
            if len(password) < 3:
                return {"error": "Password must be at least 3 characters long"}

            hashed_password = generate_password_hash(password)

            new_user = User(
                full_name=full_name,
                phone=phone,
                login=login,
                password=hashed_password,
                user_type=user_type,
            )

            db.session.add(new_user)
            db.session.commit()

            return new_user.to_dict()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def delete_user(user_id):
        try:
            from models.user import User

            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            db.session.delete(user)
            db.session.commit()

            return {"message": "User deleted successfully"}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
