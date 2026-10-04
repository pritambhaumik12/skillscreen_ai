from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models.user import User
from app.models.profile import StudentProfile
from app.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
        
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    role = request.form.get('role', 'employee')
    
    if not email or not password or not name:
        flash("Missing required fields", "error")
        return render_template('register.html')
        
    if password != confirm_password:
        flash("Passwords do not match", "error")
        return render_template('register.html')
        
    if User.query.filter_by(email=email).first():
        flash("Email already exists", "error")
        return render_template('register.html')
        
    dob_str = request.form.get('date_of_birth')
    dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        gender=request.form.get('gender'),
        phone=request.form.get('phone'),
        date_of_birth=dob
    )
    db.session.add(user)
    db.session.commit()
    
    if role == 'employee':
        profile = StudentProfile(
            user_id=user.id,
            job_experience=request.form.get('job_experience'),
            job_roles=request.form.get('job_roles'),
            company_names=request.form.get('company_names')
        )
        db.session.add(profile)
        db.session.commit()
        
    flash("User registered successfully. Please login.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['role'] = user.role
        flash("Login successful!", "success")
        return redirect(url_for('main.dashboard'))
        
    flash("Invalid credentials", "error")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
