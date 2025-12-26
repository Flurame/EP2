from flask import Blueprint, request, jsonify

from middleware.auth_middleware import require_auth
from services.user_service import UserService
from models.user import User
from database import db

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# ============================================================================
# GET /api/users/        - Получить всех пользователей (только Менеджер)
# ============================================================================
@users_bp.route("/", methods=["GET"])
@require_auth
def get_all_users(current_user):
    """Получить всех пользователей (только для Менеджера)."""
    try:
        if current_user.get("user_type") != "Менеджер":
            return (
                jsonify(
                    {
                        "error": "Permission denied - only Manager can view all users"
                    }
                ),
                403,
            )

        result = UserService.get_all_users()
        return jsonify({"data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# GET /api/users/<int:user_id>  - Получить одного пользователя
# ============================================================================
@users_bp.route("/<int:user_id>", methods=["GET"])
@require_auth
def get_user(user_id, current_user):
    """Получить информацию о пользователе."""
    try:
        # Пользователь может видеть только свои данные, Менеджер видит всех
        if current_user.get("user_type") != "Менеджер" and current_user.get(
            "user_id"
        ) != user_id:
            return jsonify({"error": "Permission denied"}), 403

        result = UserService.get_user_by_id(user_id)
        if result is None:
            return jsonify({"error": "User not found"}), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# GET /api/users/specialists  - Получить всех специалистов
# ============================================================================
@users_bp.route("/specialists", methods=["GET"])
@require_auth
def get_specialists(current_user):
    """Получить всех специалистов."""
    try:
        result = UserService.get_specialists()
        return jsonify({"data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# POST /api/users/        - Создать нового пользователя (только Менеджер)
# ============================================================================
@users_bp.route("/", methods=["POST"])
@require_auth
def create_user(current_user):
    """
    Создать нового пользователя (только Менеджер).

    Ожидаемый JSON:
    {
      "full_name": "Иван Петров",
      "phone": "89991234567",
      "login": "ivan_petrov",
      "password": "secret123",
      "user_type": "Специалист"
    }
    """
    try:
        if current_user.get("user_type") != "Менеджер":
            return (
                jsonify(
                    {
                        "error": "Permission denied - only Manager can add users"
                    }
                ),
                403,
            )

        data = request.get_json() or {}
        required_fields = ["full_name", "phone", "login", "password"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        result = UserService.create_user(
            full_name=data["full_name"],
            phone=data["phone"],
            login=data["login"],
            password=data["password"],
            user_type=data.get("user_type", "Заказчик"),
        )

        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 400

        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# DELETE /api/users/<int:user_id>  - Удалить пользователя (только Менеджер)
# ============================================================================
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@require_auth
def delete_user(user_id, current_user):
    """Удалить пользователя (только Менеджер)."""
    try:
        if current_user.get("user_type") != "Менеджер":
            return (
                jsonify(
                    {
                        "error": "Permission denied - only Manager can delete users"
                    }
                ),
                403,
            )

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Нельзя удалить себя
        if user_id == current_user.get("user_id"):
            return jsonify({"error": "Cannot delete yourself"}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully", "user_id": user_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PUT /api/users/<int:user_id>  - Обновить пользователя
# ============================================================================
@users_bp.route("/<int:user_id>", methods=["PUT"])
@require_auth
def update_user(user_id, current_user):
    """Обновить данные пользователя."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Пользователь может обновлять только свои данные, Менеджер может обновлять всех
        if current_user.get("user_type") != "Менеджер" and current_user.get(
            "user_id"
        ) != user_id:
            return jsonify({"error": "Permission denied"}), 403

        data = request.get_json() or {}

        if "full_name" in data:
            user.full_name = data["full_name"]
        if "phone" in data:
            user.phone = data["phone"]
        if "password" in data:
            from werkzeug.security import generate_password_hash

            user.password = generate_password_hash(data["password"])

        # Только Менеджер может менять роль
        if "user_type" in data and current_user.get("user_type") == "Менеджер":
            user.user_type = data["user_type"]

        db.session.commit()

        return jsonify({"message": "User updated successfully", "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
