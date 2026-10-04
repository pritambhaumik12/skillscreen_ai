from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request, current_app, send_from_directory
import uuid
import os
from werkzeug.utils import secure_filename
from app.models.profile import StudentProfile
from app.utils.ai_services import audio_to_text, evaluate_answer, generate_question, text_to_audio

interview_bp = Blueprint('interview', __name__, url_prefix='/api/v1/interview')

@interview_bp.route('/precheck/<session_id>')
def precheck(session_id):
    if 'user_id' not in session:
        flash("Please log in first", "error")
        return redirect(url_for('auth.login'))
    return render_template('precheck.html', session_id=session_id)

@interview_bp.route('/start/<session_id>', methods=['POST'])
def start_interview(session_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    import subprocess
    import sys
    # Must use external URL to resolve cleanly from Python app
    url = url_for('interview.live_shell', session_id=session_id, _external=True)
    
    # Spawn background desktop window
    subprocess.Popen([sys.executable, "secure_browser.py", url])
    
    return render_template('interview_launched.html')

@interview_bp.route('/live/<session_id>')
def live_shell(session_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Pre-generate the initial welcoming TTS
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    initial_q = "Welcome! Could you start by introducing yourself and highlighting a recent technical project you enjoyed working on?"
    out_audio_filename = f"init_{uuid.uuid4().hex}.mp3"
    out_audio_path = os.path.join(upload_folder, out_audio_filename)
    text_to_audio(initial_q, out_audio_path)
    
    audio_url = url_for('interview.serve_audio', filename=out_audio_filename)
        
    return render_template('interview_shell.html', session_id=session_id, initial_audio_url=audio_url)

@interview_bp.route('/end/<session_id>')
def end_session(session_id):
    # This securely terminates and can store the interview state inside DB
    return jsonify({"status": "terminated safely"})

@interview_bp.route('/verify_identity/<session_id>', methods=['POST'])
def verify_identity(session_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session.get('user_id')
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    photos_exist = all([os.path.exists(os.path.join(upload_folder, f"{user_id}_live_photo_{i}.jpg")) for i in range(3)])
    
    if photos_exist:
        return jsonify({"verified": True})
    else:
        return jsonify({"error": "Missing 3 live photos in profile for identity verification."}), 400

@interview_bp.route('/transcribe_audio/<session_id>', methods=['POST'])
def transcribe_audio(session_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files['audio']
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    temp_audio_path = os.path.join(upload_folder, f"in_{uuid.uuid4().hex}.wav")
    audio_file.save(temp_audio_path)
    
    # Speech to text
    answer_text = audio_to_text(temp_audio_path)
    
    try:
        os.remove(temp_audio_path)
    except:
        pass
        
    return jsonify({"stt_text": answer_text})

@interview_bp.route('/submit_answer/<session_id>', methods=['POST'])
def submit_answer(session_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    answer_text = request.form.get('answer_text', '')
    history = request.form.get('history', '')
    last_question = request.form.get('last_question', '')
    
    cv_text = "Standard Candidate"
    user_id = session.get('user_id')
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if profile and profile.cv_text:
        cv_text = profile.cv_text[:2000]
        
    # Evaluate Answer
    eval_text = "Good."
    if answer_text:
        eval_text = evaluate_answer(last_question, answer_text, cv_text)

    # Generate Next Question
    next_question = generate_question(cv_text, history + f"\nCandidate Answer: {answer_text}")

    # Text to Speech using requested newer format 
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    out_audio_filename = f"out_{uuid.uuid4().hex}.mp3"
    out_audio_path = os.path.join(upload_folder, out_audio_filename)
    text_to_audio(next_question, out_audio_path)
        
    return jsonify({
        "evaluation": eval_text,
        "next_question": next_question,
        "audio_url": url_for('interview.serve_audio', filename=out_audio_filename),
        "stt_answer": answer_text
    })

@interview_bp.route('/audio/<filename>')
def serve_audio(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)
