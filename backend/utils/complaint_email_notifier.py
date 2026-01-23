import smtplib
from email.mime.text import MIMEText
from flask import current_app
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
    msg['From'] = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    msg['To'] = config.to_email

    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            if config.cc_email:
                msg['Cc'] = config.cc_email
                server.send_message(msg)
    except Exception as e:
        # Log error but don't crash the complaint submission
        current_app.logger.error(f"Failed to send complaint email: {str(e)}")