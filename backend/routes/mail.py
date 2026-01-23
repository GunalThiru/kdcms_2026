from flask import Blueprint, request, jsonify
from backend.services.mail_service import send_complaint_mail

mail_bp = Blueprint("mail", __name__, url_prefix="/mail")

@mail_bp.route("/send/<int:complaint_id>", methods=["POST"])
def send_mail(complaint_id):
    try:
        result = send_complaint_mail(
            complaint_id=complaint_id,
            sent_by=request.json.get("sent_by")  # staff user id
        )
        return jsonify({"message": "Mail sent", "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
