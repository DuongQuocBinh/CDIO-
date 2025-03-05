from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from .models import db, User, Doctor, Appointment, HealthTip, Payment, Message

