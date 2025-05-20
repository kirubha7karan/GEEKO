from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes.chatbot import app as bp
    app.register_blueprint(bp)

    app.secret_key = 'geekoStar'
    
    return app
