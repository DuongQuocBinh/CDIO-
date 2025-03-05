from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

db = SQLAlchemy()  # Chỉ khai báo db mà không gắn app
mysql = MySQL() 