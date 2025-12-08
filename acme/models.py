from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Salary_developer(db.Model):
    __tablename__ = "salary_developer"
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String)
    salary = db.Column(db.Integer)

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('salary_developer.id'))  # исправить имя поля
    results = db.Column(db.JSON)  # новое поле для хранения всех результатов
    analysis_time = db.Column(db.DateTime, default=datetime.utcnow)
    file = db.relationship('Salary_developer', back_populates='analysis_results')

