from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.users import User
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
import pytz

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

# helper
def ist_dt():
    
    return datetime.now(pytz.timezone("Asia/Kolkata")).replace(tzinfo=None)
# -------------------------
# Signup Route
# -------------------------
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    name = data.get('name')
    password = data.get('password')
    dob = data.get('dob')

    if not name or not password or not dob:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid DOB format. Use YYYY-MM-DD"}), 400

    new_user = User(
        name=name,
        dob=dob_date,
        age=data.get('age', 23),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        password_hash=password,
        role=data.get('role', 'customer'),
        gender=data.get('gender', ''),
        is_online=False,
        last_seen=datetime.now(timezone.utc)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201


# -------------------------
# Login Route
# -------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
   

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.password_hash == password:
        user.is_online = True
        user.last_seen = ist_dt()
        db.session.commit()
        

        access_token = create_access_token(identity= str(user.id) )

        return jsonify({    
            'message': 'Login successful!',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401


# -------------------------
# Logout Route
# -------------------------
@auth_bp.route('/logout', methods=['POST'])

def logout():
    data = request.get_json()
    user_id = data.get("user_id")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_online = False
    user.last_seen = ist_dt()
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200
