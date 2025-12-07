from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base


db = SQLAlchemy()

class Salary_manager(db.Model):
    __tablename__ = "salary_manager"
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String)
    salary = db.Column(db.Integer)

    analysis_results = db.relationship('AnalysisResult', back_populates='file')


class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('salary_manager.id'))  # исправить имя поля
    results = db.Column(db.JSON)  # новое поле для хранения всех результатов
    analysis_time = db.Column(db.DateTime, default=datetime.utcnow)

    file = db.relationship('Salary_manager', back_populates='analysis_results')
