from backend.extensions import db

class ComplaintEmailConfig(db.Model):
    __tablename__ = 'complaint_email_config'

    id = db.Column(db.BigInteger, primary_key=True)

    problem_type = db.Column(db.String(50), nullable=False)
    sub_problem_type = db.Column(db.String(50), nullable=False)

    to_email = db.Column(db.String(255), nullable=False)
    cc_email = db.Column(db.String(255))

    department_id = db.Column(
        db.BigInteger,
        db.ForeignKey('departments.id'),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True)

    # relationship
    department = db.relationship(
        'Department',
        back_populates='email_configs'
    )
