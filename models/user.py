from database import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'login': self.login,
            'user_type': self.user_type
        }

