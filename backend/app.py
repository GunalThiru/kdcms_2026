import os
from dotenv import load_dotenv
load_dotenv()

print("Environment Variables Loaded:")
print("FAST2SMS_API_KEY =", bool(os.getenv("FAST2SMS_API_KEY")))    
print("FAST2SMS_URL =", os.getenv("FAST2SMS_URL"))
print("FAST2SMS_SENDER =", os.getenv("FAST2SMS_SENDER"))
print("MAIL_USERNAME =", os.getenv("MAIL_USERNAME"))
print("MAIL_PASSWORD =", bool(os.getenv("MAIL_PASSWORD")))

from flask import Flask, request, make_response
from flask_cors import CORS
from backend.extensions import db, jwt, mail
from backend.routes import register_routes
from backend.config import config

def create_app(config_name="default"):
    app = Flask(__name__)

    # 🔥 LOAD CONFIG CLASS
    app.config.from_object(config[config_name])

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
