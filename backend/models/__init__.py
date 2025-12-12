# backend/models/__init__.py
from ..extensions import db
from .users import User
from .complaints import Complaint
from .complaint_attachments import ComplaintAttachment
from .feedback import Feedback
from .complaint_assignment import ComplaintAssignment
