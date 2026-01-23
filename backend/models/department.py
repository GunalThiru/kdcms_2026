from backend.extensions import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    official_email = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # relationships
    email_configs = db.relationship(
        'ComplaintEmailConfig',
        back_populates='department',
        lazy='dynamic'
    )

    email_logs = db.relationship(
        'ComplaintEmailLog',
        back_populates='department',
        lazy='dynamic'
    )
