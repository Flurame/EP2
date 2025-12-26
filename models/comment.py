from database import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.Text, nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('repair_requests.request_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'message': self.message,
            'master_id': self.master_id,
            'request_id': self.request_id,
            'created_at': str(self.created_at) if self.created_at else None
        }
