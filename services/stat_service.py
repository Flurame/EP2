from database import db
from sqlalchemy import func

class StatisticsService:
    @staticmethod
    def get_completed_requests_count():
        try:
            from models.repair_request import RepairRequest
            count = RepairRequest.query.filter_by(request_status='Готова к выдаче').count()
            return {'completed_requests_count': count}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_average_completion_time():
        try:
            from models.repair_request import RepairRequest
            requests = RepairRequest.query.filter(RepairRequest.completion_date.isnot(None)).all()
            if not requests:
                return {'avg_completion_days': 0}
            total_days = sum((r.completion_date - r.start_date).days for r in requests)
            return {'avg_completion_days': round(total_days / len(requests))}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_statistics_by_equipment_type():
        try:
            from models.repair_request import RepairRequest
            equipment_types = db.session.query(
                RepairRequest.climate_tech_type,
                func.count(RepairRequest.request_id).label('total_requests')
            ).group_by(RepairRequest.climate_tech_type).all()
            result = [{'equipment_type': eq[0], 'total_requests': eq[1]} for eq in equipment_types]
            return result
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_specialist_workload():
        try:
            from models.repair_request import RepairRequest
            from models.user import User
            specialists = db.session.query(User).filter_by(user_type='Специалист').all()
            result = []
            for specialist in specialists:
                assigned = RepairRequest.query.filter_by(master_id=specialist.user_id).count()
                result.append({
                    'specialist_id': specialist.user_id,
                    'specialist_name': specialist.full_name,
                    'total_assigned': assigned
                })
            return result
        except Exception as e:
            return {'error': str(e)}
