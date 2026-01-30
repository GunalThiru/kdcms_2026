# backend/models/__init__.py
from ..extensions import db
from .users import User
from .complaints import Complaint
from .complaint_attachments import ComplaintAttachment
from .feedback import Feedback
from .complaint_assignment import ComplaintAssignment
from .reporting_staff import ReportingStaff
from .complaint_status_master import ComplaintStatus
from .complaint_views import ComplaintView
from .department import Department
from .complaint_email_config import ComplaintEmailConfig
from .complaint_email_log import ComplaintEmailLog
from .email_templates import EmailTemplate
from .registered_by_type_master import RegisteredByTypeMaster

