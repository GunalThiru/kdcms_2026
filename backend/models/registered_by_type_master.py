from backend.extensions import db

class RegisteredByTypeMaster(db.Model):
    __tablename__ = 'registered_by_type_master'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # reverse relationship
    complaints = db.relationship(
        'Complaint',
        back_populates='registered_by_type'
    )

    def __repr__(self):
        return f"<RegisteredByType {self.code}>"
