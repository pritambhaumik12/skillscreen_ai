import sys
import os
import subprocess

try:
    import webview
except ImportError:
    print("Installing pywebview for secure browser...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
    import webview

class Api:
    def __init__(self):
        self.window = None
        
    def close_app(self):
        if self.window:
            self.window.destroy()

def main():
    if len(sys.argv) < 2:
        print("URL required")
        sys.exit(1)
    
    url = sys.argv[1]
    
    api = Api()
    
    # Create the secure window
    # Fullscreen lock-down browser for the interview
    window = webview.create_window(
        'SkillScreen AI - Secure Interview Evaluation',
        url,
        fullscreen=True,
        frameless=False,
        text_select=False,
        confirm_close=True,
        js_api=api
    )
    api.window = window
    
    try:
        # Pass private_mode=False so cookies/sessions can be carried over 
        # (Though Flask might require re-auth if session cookie isn't shared. 
        # If needed, the candidate logs in on the pop-up or inherits session).
        webview.start(private_mode=False)
    except Exception as e:
        print(f"Failed to start secure browser: {e}")

if __name__ == '__main__':
    main()
