from backend.extensions import db


class ComplaintEmailLog(db.Model):
    __tablename__ = 'complaint_email_log'

    id = db.Column(db.BigInteger, primary_key=True)

    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey('complaints.id'),
        nullable=False
    )

    sent_by = db.Column(db.Integer, nullable=False)

    to_email = db.Column(db.String(255), nullable=False)
    cc_email = db.Column(db.String(255))

    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.Enum('sent', 'failed', 'queued', 'retry'),
        default='queued'
    )

    department_id = db.Column(
        db.BigInteger,
        db.ForeignKey('departments.id'),
        nullable=True
    )

    error_message = db.Column(db.Text)

    # relationships
    department = db.relationship(
        'Department',
        back_populates='email_logs'
    )

    complaint = db.relationship(
        'Complaint',
        back_populates='email_logs'
    )

