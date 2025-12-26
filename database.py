from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_db():
    from flask import g
    if 'db' not in g:
        from config import Config
        from sqlalchemy import create_engine
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        g.db = Session()
    return g.db