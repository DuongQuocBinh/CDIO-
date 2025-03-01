from flask_sqlalchemy import SQLAlchemy
from .models import db, User, Doctor, Appointment, HealthTip, Payment, Message

db = SQLAlchemy()


__all__ = ["db", "User", "Doctor", "Appointment", "HealthTip", "Payment", "Message"]
