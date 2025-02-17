from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(36), unique=True, nullable=False)
    message = db.Column(db.String(255), nullable=False)

def log_action(file_id, message):
    new_log = Log(file_id=file_id, message=message)
    db.session.add(new_log)
    db.session.commit()

# app/repositories/log_repository.py
def save_log(file_id, message):
    from modules.database import log_action
    log_action(file_id, message)
