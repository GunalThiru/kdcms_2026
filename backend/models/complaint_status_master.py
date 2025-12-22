from backend.extensions import db


class ComplaintStatus(db.Model):
    __tablename__ = "complaint_status_master"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    complaints = db.relationship("Complaint", back_populates="status")
