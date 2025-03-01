from flask import Blueprint, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from extensions import mysql 

# Khai báo Blueprint
auth_bp = Blueprint('auth', __name__)

# Cấu hình MySQL sẽ được nhận từ app.py
mysql = None  

def init_mysql(app):
    global mysql
    mysql = MySQL(app)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import mysql
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT MaBacSi,email, password FROM doctor_account WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[1], password):
            session['doctor_id'] = user[0]
            flash('Đăng nhập thành công!', 'success')
            return redirect('/dashboard')  # Điều hướng đến trang dashboard
        else:
            flash('Sai email hoặc mật khẩu!', 'danger')

    return render_template('dashboard.html')

@auth_bp.route('/dashboard')
def dashboard_bacsi():
    if 'doctor_id' in session:
        return "Chào mừng bác sĩ! Đây là trang dashboard."
    else:
        return redirect('/login')

@auth_bp.route('/logout')
def logout():
    session.pop('doctor_id', None)
    flash('Bạn đã đăng xuất!', 'info')
    return redirect('/login')
