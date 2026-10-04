import os
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import tempfile
import json
import re
def configure_gemini():
    api_key = os.environ.get('GEMINI_API_KEY', 'key_xyz')
    genai.configure(api_key=api_key)

def get_gemini_model():
    configure_gemini()
    return genai.GenerativeModel('gemini-3.8-flash')

def generate_question(cv_text, conversation_history=""):
    try:
        model = get_gemini_model()
        prompt = f"Based on the following candidate CV context:\n{cv_text}\n\nRecent conversation history:\n{conversation_history}\n\nAsk a single, relevant technical or behavioral interview question suitable for this candidate. Only output the question."
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Could not generate question."
    except Exception as e:
        print(f"Gemini Question Gen Error: {e}")
        return "Could you please elaborate on your recent project experience?"

def evaluate_answer(question, answer, cv_text):
    try:
        model = get_gemini_model()
        prompt = f"Question: {question}\nCandidate Answer: {answer}\nCV Context: {cv_text}\n\nEvaluate the answer briefly (1-2 sentences). State if it is good or needs improvement, and why."
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Thank you for your answer."
    except Exception as e:
        print(f"Gemini Eval Error: {e}")
        return "Thank you for that response."

def audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            # Use google web speech api for basic free stt
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"STT Error: {e}")
        return ""

def text_to_audio(text, output_path):
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', tld='us', slow=False)
        tts.save(output_path)
        return output_path
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gTTS"])
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', tld='us', slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def extract_cv_tags(cv_text):
    try:
        model = get_gemini_model()
        prompt = f"Analyze this CV text:\n{cv_text}\n\nExtract key information and return it strictly as a JSON object with exactly the following keys (arrays of strings): 'skills', 'projects', 'subjects_of_interest', 'tools', 'libraries', 'frameworks'. If any category has no data, return an empty array for that key. Do not output anything other than standard JSON format without backticks."
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        return json.loads(content.strip())
    except Exception as e:
        print(f"Gemini Tag Extraction Error: {e}")
        return {}
