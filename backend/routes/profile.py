from flask import Blueprint, request, jsonify
from backend.models import db, User
from datetime import datetime

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


# -------------------------
# GET PROFILE
# -------------------------
@profile_bp.route("/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "gender": user.gender,
        "dob": user.dob.isoformat() if user.dob else None,
        "age": user.age,
        "is_online": user.is_online
    }), 200


# -------------------------
# UPDATE PROFILE
# -------------------------
@profile_bp.route("/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    if "name" in data:
        user.name = data["name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "gender" in data:
        user.gender = data["gender"]
    if "age" in data:
        user.age = data["age"]
    if "dob" in data and data["dob"]:
        user.dob = datetime.strptime(data["dob"], "%Y-%m-%d")

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200
