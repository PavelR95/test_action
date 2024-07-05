import flask_app

if __name__ == "__main__":
    # Create a change in run.py
    app = flask_app.initial_app()
    app.run(port=5000)
