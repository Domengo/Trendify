from flask import Blueprint, request, jsonify
from src.auth import register, login, google_login

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    if not data or not all(
                            key in data for key in
                            ("username", "password", "role")
                            ):
        return jsonify({"message": "Missing required fields"}), 400
    try:        
        return register(data["username"], data["password"], data["role"])
    except ValueError as e:        
        return jsonify({"message": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()    
    if not data or not all(key in data for key in ("username", "password")):        
        return jsonify({"message": "Missing username or password"}), 400
    try:
        token = login(data["username"], data["password"])
        if token:
            return jsonify({"token": token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@auth_bp.route("/login/google", methods=["POST"])
def login_user_google():
    data = request.get_json()
    if not data or "token" not in data:
        return jsonify({"message": "Missing Google token"}), 400
    try:
        token = google_login(data["token"])
        if token:
            return jsonify({"token": token}), 200
        return jsonify({"message": "Google authentication failed"}), 401
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
