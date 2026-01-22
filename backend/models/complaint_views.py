# backend/models/complaint_view.py

from datetime import datetime
from backend.models import db

class ComplaintView(db.Model):
    __tablename__ = 'complaint_views'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey('complaints.id', ondelete='CASCADE'),
        nullable=False
    )
    viewed_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    viewed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Optional but VERY useful relationships
    complaint = db.relationship(
        'Complaint',
        backref=db.backref('views', lazy='dynamic', cascade='all, delete-orphan')
    )

    viewer = db.relationship(
        'User',
        backref=db.backref('complaint_views', lazy='dynamic')
    )
