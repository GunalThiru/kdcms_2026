import os
from dotenv import load_dotenv
load_dotenv() # Loading environment variables from .env file before creating the app
    

print("MAIL_USERNAME =", os.environ.get("MAIL_USERNAME"))
print("MAIL_PASSWORD =", os.environ.get("MAIL_PASSWORD"))


from flask import Flask, request, make_response
from flask_cors import CORS
from backend.extensions import db, jwt, mail
from backend.routes import register_routes
from backend.config import config





def create_app():
    
    app = Flask(__name__)

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/kdmbcms"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Connection pooling and timeout settings for reliability
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,  # Test connection before using
        "connect_args": {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
        }
    }

    # 🔐 JWT CONFIG (THIS FIXES YOUR ERROR)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change later
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    # 📧 MAIL CONFIG (Load from environment variables)
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True
    )

    # Handle OPTIONS preflight
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response

    # -------------------------------------------------
    # INIT EXTENSIONS
    # -------------------------------------------------
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)   # 🔥 Initialize Flask-Mail with app config

    # -------------------------------------------------
    # ROUTES
    # -------------------------------------------------
    register_routes(app)

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize database: {e}")
            print("Start MySQL and restart the app to enable database features.")

    return app



app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
