from backend.extensions import db

class EmailTemplate(db.Model):
    __tablename__ = 'email_templates'

    id = db.Column(db.BigInteger, primary_key=True)
    template_key = db.Column(db.String(50), unique=True, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
