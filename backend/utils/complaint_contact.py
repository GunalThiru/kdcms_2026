def get_complaint_contact_mobile(complaint):
    code = complaint.registered_by_type.code

    if code == "guest":
        return complaint.guest_mobile

    if code == "staff":
        return complaint.guest_mobile  # customer mobile entered by staff

    if code == "customer":
        return complaint.reporter.mobile if complaint.reporter else None

    return None
def get_complaint_contact_email(complaint):
    code = complaint.registered_by_type.code

    if code == "guest":
        return complaint.guest_email

    if code == "staff":
        return complaint.guest_email  # customer email entered by staff

    if code == "customer":
        return complaint.reporter.email if complaint.reporter else None

    return None 