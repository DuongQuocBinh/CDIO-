from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from auth import auth_bp
from flask_mysqldb import MySQL
from models import db, User, Doctor, Appointment, HealthTip, Payment, Message
from extensions import mysql

app = Flask(__name__)

app.config.from_object(Config)

#Cấu hình mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'healhub'

mysql.init_app(app)  # Gắn MySQL vào app Flask

# Cấu hình session
app.secret_key = "your_secret_key"

# Khởi tạo SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/healhub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy()

db.init_app(app)

# Đăng ký Blueprint
app.register_blueprint(auth_bp)


# Tạo database nếu chưa có
with app.app_context():
    db.create_all()

# Trang chủ
@app.route('/')
def home():
    return render_template("index.html")

# API Đăng ký
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        return redirect(url_for("home"))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email đã tồn tại, vui lòng đăng nhập!", "warning")
        return redirect(url_for("home"))

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
    return redirect(url_for("home"))

# API Đăng nhập
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"message": "Vui lòng nhập email và mật khẩu!", "status": "error"}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({
            "message": "Đăng nhập thành công!",
            "status": "success",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        })
    else:
        return jsonify({"message": "Sai tài khoản hoặc mật khẩu!", "status": "error"}), 401

    # Đăng nhập trang web
    @app.route('/login', methods=['POST'])
    def login():
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            flash("Vui lòng nhập email và mật khẩu!", "danger")
            return redirect(url_for("home"))

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash(f"Chào mừng {user.name}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "danger")
            return redirect(url_for("home"))

# Trang dashboard
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id') 
    if 'user_id':
        user = User.query.get(session['user_id'])
    if user:
        return render_template("dashboard.html", user=user)

    flash("Bạn cần đăng nhập để truy cập!", "warning")
    return redirect(url_for("home"))

# Đặt lịch khám
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session:
        flash("Bạn cần đăng nhập để đặt lịch khám!", "warning")
        return redirect(url_for("home"))
    
    doctor_id = request.form.get("doctor_id")
    appointment_time = request.form.get("appointment_time")
    new_appointment = Appointment(user_id=session['user_id'], doctor_id=doctor_id, appointment_time=appointment_time)
    db.session.add(new_appointment)
    db.session.commit()
    flash("Đặt lịch khám thành công!", "success")
    return redirect(url_for("dashboard"))

# Quản lý bác sĩ
@app.route('/doctors')
def list_doctors():
    doctors = Doctor.query.all()
    return render_template("doctors.html", doctors=doctors)

@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    name = request.form.get("name")
    khoa_cong_tac = request.form.get("khoa_cong_tac")
    gio_lam_viec = request.form.get("gio_lam_viec")
    new_doctor = Doctor(name=name, khoa_cong_tac=khoa_cong_tac, gio_lam_viec=gio_lam_viec)
    db.session.add(new_doctor)
    db.session.commit()
    flash("Thêm bác sĩ thành công!", "success")
    return redirect(url_for("list_doctors"))

@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    doctor = Doctor.query.get(id)
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
        flash("Xóa bác sĩ thành công!", "success")
    return redirect(url_for("list_doctors"))

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Bạn đã đăng xuất!", "info")
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
