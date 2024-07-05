import flask_app

if __name__ == "__main__":
    app = flask_app.initial_app()
    app.run(port=5000)
