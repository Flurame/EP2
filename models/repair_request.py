from database import db
from datetime import datetime

class RepairRequest(db.Model):
    __tablename__ = 'repair_requests'

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    start_date = db.Column(db.Date, nullable=False)
    climate_tech_type = db.Column(db.String(100), nullable=False)
    climate_tech_model = db.Column(db.String(100), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    request_status = db.Column(db.String(50), nullable=False)

    completion_date = db.Column(db.Date)
    repair_parts = db.Column(db.String(255))

    # ответственный мастер
    master_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # клиент
    client_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def to_dict(self):
        return {
            'request_id': self.request_id,
            'start_date': str(self.start_date),
            'climate_tech_type': self.climate_tech_type,
            'climate_tech_model': self.climate_tech_model,
            'problem_description': self.problem_description,
            'request_status': self.request_status,
            'completion_date': str(self.completion_date) if self.completion_date else None,
            'repair_parts': self.repair_parts,
            'master_id': self.master_id,
            'client_id': self.client_id,
        }
