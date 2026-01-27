from flask_mail import Message
from backend.extensions import db, mail
from backend.models import (
    Complaint,
    ComplaintEmailConfig,
    ComplaintEmailLog,
    ComplaintAttachment,
    EmailTemplate
)
import os

def send_complaint_mail(complaint_id, template_key='complaint_received', sent_by=None):
    """
    Send email using template with dynamic variables
    template_key: 'complaint_received', 'complaint_resolved', etc.
    """
    if not sent_by:
        sent_by = "SYSTEM"

    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Get email template
    template = EmailTemplate.query.filter_by(
        template_key=template_key,
        is_active=True
    ).first()
    
    if not template:
        raise Exception(f"Email template '{template_key}' not found or inactive")

    # Get email config
    config = ComplaintEmailConfig.query.filter_by(
        problem_type=complaint.problem_type,
        sub_problem_type=complaint.sub_problem_type,
        is_active=1
    ).first()

    if not config:
        config = ComplaintEmailConfig.query.filter_by(
            problem_type=complaint.problem_type,
            is_active=1
        ).first()

    if not config:
        raise Exception(f"No email config found for {complaint.problem_type}")

    # Prepare variables for template
    template_vars = {
        'complaint_no': complaint.complaint_no,
        'problem_type': complaint.problem_type,
        'sub_problem_type': complaint.sub_problem_type,
        'problem_description': complaint.problem_description,
        'reporter_name': complaint.reporter_name or 'Guest',
        'date_of_issue': complaint.date_of_issue.isoformat() if complaint.date_of_issue else 'N/A',
        'reporting_mode': complaint.reporting_mode or 'N/A',
        'solution_provided': complaint.solution_provided or 'Pending',
        'guest_mobile': complaint.guest_mobile,
        'guest_email': complaint.guest_email
    }

    # Replace variables in subject and body
    subject = template.subject
    body = template.body
    
    for key, value in template_vars.items():
        subject = subject.replace(f"{{{{{key}}}}}", str(value))
        body = body.replace(f"{{{{{key}}}}}", str(value))

    msg = Message(
    subject=subject,
    recipients=[config.to_email],
    cc=[config.cc_email] if config.cc_email else None
    )

    msg.html = body   # 👈 HTML EMAIL


    # 📎 ATTACH FILES
    attachments = ComplaintAttachment.query.filter_by(complaint_id=complaint_id).all()
    for attachment in attachments:
        file_path = os.path.join("uploads/complaints", attachment.filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    msg.attach(attachment.filename, attachment.file_type, f.read())
            except Exception as e:
                print(f"Warning: Could not attach file {attachment.filename}: {str(e)}")

    try:
        mail.send(msg)
        status = "sent"
        error = None
    except Exception as e:
        status = "failed"
        error = str(e)

    log = ComplaintEmailLog(
        complaint_id=complaint.id,
        sent_by=sent_by,
        to_email=config.to_email,
        cc_email=config.cc_email,
        subject=subject,
        body=body,
        status=status,
        error_message=error
    )

    db.session.add(log)
    db.session.commit()

    return {"status": status}