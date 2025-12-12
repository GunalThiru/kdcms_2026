def register_routes(app):
    from .auth import auth_bp
    # from .user import user_bp
    from .complaint_form import complaint_bp
    from .complaint_attachment import attachment_bp
    # from .feedback import feedback_bp

    app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)
    app.register_blueprint(complaint_bp)
    # app.register_blueprint(feedback_bp)
    app.register_blueprint(attachment_bp)

    @app.route("/")
    def home():
         return {"message": "Backend API is running"}, 200

