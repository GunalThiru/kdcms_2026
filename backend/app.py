from flask import Flask, request, make_response
from flask_cors import CORS
from backend.models import db
from backend.routes import register_routes
from backend.extensions import db
from backend.models import User, Complaint, ComplaintAttachment, Feedback, ComplaintAssignment


def create_app():
    app = Flask(__name__)

    # DB config
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/kdmbcms"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Handle OPTIONS preflight for all routes
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response

    db.init_app(app)
    register_routes(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
