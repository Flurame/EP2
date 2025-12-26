from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_auth, require_role
from models.repair_request import RepairRequest
from database import db
from datetime import date, datetime

requests_bp = Blueprint('requests', __name__, url_prefix='/api/requests')

# ============================================================================
# GET /api/requests/ - Получить все заявки
# ============================================================================
@requests_bp.route('/', methods=['GET'])
@require_auth
def get_all_requests(current_user):
    """Получить все заявки (в зависимости от роли)"""
    try:
        # ✅ page оставляем как есть
        page = request.args.get('page', 1, type=int)

        # ✅ ВАЖНО: если limit не передали — показываем все записи
        limit_raw = request.args.get('limit', None)  # было 10 по умолчанию
        status = request.args.get('status', None)
        search = request.args.get('search', None)

        query = RepairRequest.query

        # Для Заказчиков показываем только их заявки
        if current_user.get('user_type') == 'Заказчик':
            query = query.filter_by(client_id=current_user.get('user_id'))

        # Фильтр по статусу
        if status:
            query = query.filter_by(request_status=status)

        # Поиск по ID
        if search:
            try:
                query = query.filter_by(request_id=int(search))
            except ValueError:
                pass

        # ✅ Чтобы новые были сверху (иначе “11-я” может не быть на первой странице)
        query = query.order_by(RepairRequest.request_id.desc())

        # ------------------------------
        # Режим "показать все"
        # ------------------------------
        if limit_raw is None or str(limit_raw).lower() in ('0', 'all', 'none'):
            items = query.all()
            total = len(items)

            return jsonify({
                'data': [{
                    'request_id': r.request_id,
                    'start_date': r.start_date.isoformat() if r.start_date else None,
                    'climate_tech_type': r.climate_tech_type,
                    'climate_tech_model': r.climate_tech_model,
                    'problem_description': r.problem_description,
                    'request_status': r.request_status,
                    'completion_date': r.completion_date.isoformat() if r.completion_date else None,
                    'repair_parts': r.repair_parts,
                    'master_id': r.master_id,
                    'client_id': r.client_id
                } for r in items],
                'pagination': {
                    'page': 1,
                    'limit': total,
                    'total': total,
                    'pages': 1
                }
            }), 200

        # ------------------------------
        # Режим пагинации (как было)
        # ------------------------------
        limit = int(limit_raw)
        paginated = query.paginate(page=page, per_page=limit)

        return jsonify({
            'data': [{
                'request_id': r.request_id,
                'start_date': r.start_date.isoformat() if r.start_date else None,
                'climate_tech_type': r.climate_tech_type,
                'climate_tech_model': r.climate_tech_model,
                'problem_description': r.problem_description,
                'request_status': r.request_status,
                'completion_date': r.completion_date.isoformat() if r.completion_date else None,
                'repair_parts': r.repair_parts,
                'master_id': r.master_id,
                'client_id': r.client_id
            } for r in paginated.items],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# GET /api/requests/<int:request_id> - Получить одну заявку
# ============================================================================

@requests_bp.route('/<int:request_id>', methods=['GET'])
@require_auth
def get_request(request_id, current_user):
    """Получить информацию о заявке"""
    try:
        req = RepairRequest.query.get(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404

        # Для Заказчика - только его заявки
        if current_user.get('user_type') == 'Заказчик' and req.client_id != current_user.get('user_id'):
            return jsonify({'error': 'Access denied'}), 403

        return jsonify({
            'request_id': req.request_id,
            'start_date': req.start_date.isoformat() if req.start_date else None,
            'climate_tech_type': req.climate_tech_type,
            'climate_tech_model': req.climate_tech_model,
            'problem_description': req.problem_description,
            'request_status': req.request_status,
            'completion_date': req.completion_date.isoformat() if req.completion_date else None,
            'repair_parts': req.repair_parts,
            'master_id': req.master_id,
            'client_id': req.client_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# POST /api/requests/ - Создать заявку
# ============================================================================

@requests_bp.route('/', methods=['POST'])
@require_auth
def create_request(current_user):
    """Создать новую заявку"""
    try:
        # Проверка прав - добавлен "Менеджер по качеству"
        allowed_roles = ['Оператор', 'Специалист', 'Менеджер', 'Менеджер по качеству', 'Заказчик']
        if current_user.get('user_type') not in allowed_roles:
            return jsonify({'error': 'Permission denied'}), 403

        data = request.get_json()
        required_fields = ['climate_tech_type', 'climate_tech_model', 'problem_description', 'client_id']

        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        new_request = RepairRequest(
            start_date=date.today(),
            climate_tech_type=data['climate_tech_type'],
            climate_tech_model=data['climate_tech_model'],
            problem_description=data['problem_description'],
            request_status='Новая заявка',
            client_id=data['client_id'],
            master_id=data.get('master_id')  # можно сразу назначить ответственного
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            'message': 'Request created successfully',
            'request_id': new_request.request_id,
            'request_status': new_request.request_status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PUT /api/requests/<int:request_id> - Обновить заявку
# ============================================================================

@requests_bp.route('/<int:request_id>', methods=['PUT'])
@require_auth
def update_request(request_id, current_user):
    """Обновить заявку (Специалист, Менеджер, Менеджер по качеству)"""
    try:
        if current_user.get('user_type') not in ['Специалист', 'Менеджер', 'Менеджер по качеству']:
            return jsonify({'error': 'Permission denied'}), 403

        req = RepairRequest.query.get(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404

        data = request.get_json()

        # Обновляем только указанные поля
        if 'request_status' in data and data['request_status']:
            req.request_status = data['request_status']

        # Назначение/смена ответственного
        if 'master_id' in data:
            # Разрешаем снять назначение, если master_id == None
            req.master_id = data['master_id'] if data['master_id'] else None

        if 'repair_parts' in data and data['repair_parts'] is not None:
            req.repair_parts = data['repair_parts']

        if 'completion_date' in data and data['completion_date']:
            req.completion_date = datetime.fromisoformat(data['completion_date']).date()

        db.session.commit()

        return jsonify({
            'message': 'Request updated successfully',
            'request_id': req.request_id,
            'request_status': req.request_status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DELETE /api/requests/<int:request_id> - Удалить заявку
# ============================================================================

@requests_bp.route('/<int:request_id>', methods=['DELETE'])
@require_auth
def delete_request(request_id, current_user):
    """Удалить заявку (только Менеджер)"""
    try:
        if current_user.get('user_type') != 'Менеджер':
            return jsonify({'error': 'Permission denied - only Manager can delete'}), 403

        req = RepairRequest.query.get(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404

        db.session.delete(req)
        db.session.commit()

        return jsonify({
            'message': 'Request deleted successfully',
            'request_id': request_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
