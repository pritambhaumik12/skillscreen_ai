from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting SkillScreen AI Application...")
    app.run(debug=True, port=5000)
