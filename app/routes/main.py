from flask import Blueprint, jsonify, render_template, session, redirect, url_for, request, flash, current_app, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
if 'pypdf' in open('requirements.txt').read():
    import pypdf
else:
    pypdf = None # Though requirements.txt shows it's installed

from app.models.profile import StudentProfile
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "SkillScreen AI is running"}), 200

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    role = session.get('role')
    if role in ('student', 'employee'):
        return render_template('student_dashboard.html')
    elif role in ('recruiter', 'employer'):
        return render_template('recruiter_dashboard.html')
    else:
        return jsonify({"message": "Unknown role"})

@main_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    role = session.get('role')
    if role not in ('student', 'employee'):
        flash("Access denied.", "error")
        return redirect(url_for('main.dashboard'))
        
    user_id = session.get('user_id')
    user_profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    cv_filename = None
    if user_profile and user_profile.cv_path:
        cv_filename = os.path.basename(user_profile.cv_path)
        
    return render_template('profile.html', profile=user_profile, cv_filename=cv_filename)

@main_bp.route('/view_cv/<path:filename>')
def view_cv(filename):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)

def extract_text_from_pdf(pdf_path):
    import pypdf
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

@main_bp.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'cv_file' not in request.files:
        flash("No CV file part in the request.", "error")
        return redirect(url_for('main.profile'))
    
    file = request.files['cv_file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        flash("Please select a valid .pdf file.", "error")
        return redirect(url_for('main.profile'))
    
    if file:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, f"{uuid.uuid4().hex}_{filename}")
        file.save(file_path)
        
        # Extract text
        cv_text = ""
        if filename.lower().endswith('.pdf'):
            cv_text = extract_text_from_pdf(file_path)
        elif filename.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                cv_text = f.read()
        
        # Save to user profile
        user_id = session.get('user_id')
        profile = StudentProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = StudentProfile(user_id=user_id)
            db.session.add(profile)
        
        profile.cv_path = file_path
        profile.cv_text = cv_text
        
        from app.utils.ai_services import extract_cv_tags
        if cv_text:
            profile.ai_extracted_data = extract_cv_tags(cv_text)
            
        profile.profile_complete = True # assuming CV triggers completion
        db.session.commit()
        
        flash("CV uploaded successfully!", "success")
        return redirect(url_for('main.profile'))
    
    return redirect(url_for('main.profile'))

@main_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = StudentProfile(user_id=user_id)
        db.session.add(profile)
    
    profile.job_experience = request.form.get('job_experience')
    profile.job_roles = request.form.get('job_roles')
    profile.company_names = request.form.get('company_names')
    
    skills = request.form.get('skills')
    if skills and skills.strip():
        profile.skills_json = [s.strip() for s in skills.split(',')]
        
    projects = request.form.get('projects')
    if projects and projects.strip():
        profile.projects_json = [s.strip() for s in projects.split(',')]
        
    subjects_of_interest = request.form.get('subjects_of_interest')
    if subjects_of_interest and subjects_of_interest.strip():
        profile.subjects_of_interest_json = [s.strip() for s in subjects_of_interest.split(',')]
        
    tools = request.form.get('tools')
    if tools and tools.strip():
        profile.tools_json = [s.strip() for s in tools.split(',')]
        
    libraries = request.form.get('libraries')
    if libraries and libraries.strip():
        profile.libraries_json = [s.strip() for s in libraries.split(',')]
        
    frameworks = request.form.get('frameworks')
    if frameworks and frameworks.strip():
        profile.frameworks_json = [s.strip() for s in frameworks.split(',')]
        
    db.session.commit()
    flash('Profile details updated successfully!', 'success')
    return redirect(url_for('main.profile'))

@main_bp.route('/upload_live_photos', methods=['POST'])
def upload_live_photos():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    import base64
    user_id = session.get('user_id')
    data = request.json
    photos = data.get('photos', [])
    
    if len(photos) != 3:
        return jsonify({"error": "Please provide exactly 3 photos"}), 400
        
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    try:
        for i, photo_data in enumerate(photos):
            header, encoded = photo_data.split(",", 1)
            file_path = os.path.join(upload_folder, f"{user_id}_live_photo_{i}.jpg")
            with open(file_path, "wb") as fh:
                fh.write(base64.b64decode(encoded))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

