from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class LoginUser(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	account = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)

class EventTemp(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
	tags = db.Column(db.String(100))