from database import db

class RepairService:
    @staticmethod
    def get_all_requests():
        try:
            from models.repair_request import RepairRequest
            requests = RepairRequest.query.all()
            return [r.to_dict() for r in requests]
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_active_requests():
        try:
            from models.repair_request import RepairRequest
            active_statuses = ['Новая заявка', 'В процессе ремонта', 'Ожидание комплектующих']
            requests = RepairRequest.query.filter(RepairRequest.request_status.in_(active_statuses)).all()
            return [r.to_dict() for r in requests]
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_request_by_id(request_id):
        try:
            from models.repair_request import RepairRequest
            request = RepairRequest.query.get(request_id)
            if not request:
                return None
            return request.to_dict()
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_request(start_date, climate_tech_type, climate_tech_model, problem_description, client_id):
        try:
            from models.repair_request import RepairRequest
            new_request = RepairRequest(
                start_date=start_date,
                climate_tech_type=climate_tech_type,
                climate_tech_model=climate_tech_model,
                problem_description=problem_description,
                request_status='Новая заявка',
                client_id=client_id
            )
            db.session.add(new_request)
            db.session.commit()
            return new_request.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def update_request_status(request_id, new_status):
        try:
            from models.repair_request import RepairRequest
            request = RepairRequest.query.get(request_id)
            if not request:
                return {'error': 'Request not found'}
            request.request_status = new_status
            db.session.commit()
            return request.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    @staticmethod
    def assign_specialist(request_id, master_id):
        try:
            from models.repair_request import RepairRequest
            request = RepairRequest.query.get(request_id)
            if not request:
                return {'error': 'Request not found'}
            request.master_id = master_id
            db.session.commit()
            return request.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
