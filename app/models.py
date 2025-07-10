from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(200), nullable=False)

	def __repr__(self):
		return f'<User {self.username}>'

class Question(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	question_text = db.Column(db.String(255), nullable=False)
	option_a = db.Column(db.String(100), nullable=False)
	option_b = db.Column(db.String(100), nullable=False)
	option_c = db.Column(db.String(100), nullable=False)
	option_d = db.Column(db.String(100), nullable=False)
	correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D


class QuizResult(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	score = db.Column(db.Integer, nullable=False)
	total_questions = db.Column(db.Integer, nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

	user = db.relationship('User', backref=db.backref('results', lazy=True))