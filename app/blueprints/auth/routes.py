import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from app.extensions import db, mail
from app.models import User, UserRole
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not all([name, email, password, role]):
        return jsonify({"error": "Missing fields"}), 400

    # Validate role
    if role not in [r.value for r in UserRole]:
        return jsonify({"error": "Invalid role"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Create user and hash password
    user = User(name=name, email=email, role=UserRole(role))
    user.set_password(password)

    # Generate email verification token
    user.email_verification_token = str(uuid.uuid4())

    db.session.add(user)
    db.session.commit()

    # Send verification email
    verification_url = f"{request.host_url}api/auth/verify-email/{user.email_verification_token}"
    try:
        send_verification_email(user.email, verification_url)
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {e}")
        # optionally rollback or handle error

    return jsonify({"message": "User registered. Please check your email to verify your account."}), 201


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 400

    user.is_verified = True
    user.email_verification_token = None

    db.session.commit()

    return jsonify({"message": "Email verified successfully. You can now log in."})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token})


def send_verification_email(to_email, verification_url):
    msg = Message("Verify your email", recipients=[to_email])
    msg.body = f"Click the link to verify your email: {verification_url}"
    mail.send(msg)

    
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "is_verified": user.is_verified
    })


def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or user.role.value not in allowed_roles:
                return jsonify({"error": "Unauthorized access"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
