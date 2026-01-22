import smtplib
from email.mime.text import MIMEText
from backend.models.complaint_email_config import ComplaintEmailConfig

def notify_on_complaint_submission(complaint):
    config = ComplaintEmailConfig.query.filter_by(
        problem_type=complaint.problem_type,
        is_active=True
    ).first()

    if not config:
        return

    msg = MIMEText(
        f"New complaint received.\n\nComplaint ID: {complaint.id}"
    )
    msg['Subject'] = 'New Complaint Submitted'
    msg['From'] = 'noreply@yourdomain.com'
    msg['To'] = config.to_email

    with smtplib.SMTP('smtp.yourdomain.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
        if config.cc_email:
            msg['Cc'] = config.cc_email
            server.send_message(msg)