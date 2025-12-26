from flask import Blueprint, jsonify
from services.stat_service import StatisticsService

statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')


@statistics_bp.route('/', methods=['GET'])
def get_all_statistics():
    """Получить всю статистику"""
    try:
        completed_count = StatisticsService.get_completed_requests_count()
        average_time = StatisticsService.get_average_completion_time()
        by_equipment = StatisticsService.get_statistics_by_equipment_type()
        workload = StatisticsService.get_specialist_workload()

        return jsonify({
            'completed_requests': completed_count,
            'average_completion_time': average_time,
            'equipment_statistics': by_equipment,
            'specialist_workload': workload
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/completed-count', methods=['GET'])
def get_completed_count():
    result = StatisticsService.get_completed_requests_count()
    return jsonify(result), 200

@statistics_bp.route('/average-time', methods=['GET'])
def get_average_time():
    result = StatisticsService.get_average_completion_time()
    return jsonify(result), 200

@statistics_bp.route('/by-equipment-type', methods=['GET'])
def get_by_equipment_type():
    result = StatisticsService.get_statistics_by_equipment_type()
    return jsonify(result), 200

@statistics_bp.route('/specialist-workload', methods=['GET'])
def get_specialist_workload():
    result = StatisticsService.get_specialist_workload()
    return jsonify(result), 200
