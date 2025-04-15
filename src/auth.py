from flask import request, jsonify, Blueprint, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
from werkzeug.exceptions import Forbidden

# Replace with your actual client ID
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
SECRET_KEY = "your_secret_key"  # Replace with a strong secret key

# Helper Functions


def get_google_auth_config():
    """Get Google auth config from app settings"""
    return {
        "client_id": current_app.config.get("GOOGLE_CLIENT_ID"),
        "default_role": current_app.config.get("DEFAULT_ROLE", "influencer"),
    }


auth_bp = Blueprint("auth", __name__)


def register(username, password, role):
    from .models import User
    if User.objects(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        password=hashed_password,
        role=role or get_google_auth_config()["default_role"]
    )

    new_user.save()
    return jsonify({"message": "Registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login(username, password):
    from .models import User  # Import here to avoid circular imports

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.objects(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode(
            {"username": user.username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24), "role": user.role},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
    )

    return token if isinstance(token, str) else token.decode("utf-8")
    # if user and check_password_hash(user.password, data["password"]):
    #     token = jwt.encode(
    #         {
    #             "username": user.username,
    #             "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    #             "role": user.role,
    #         },
    #         app.config["SECRET_KEY"],
    #     )
    #     return jsonify({"token": token}), 200
    # return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route("/login/google", methods=["POST"])
def google_login():
    from .models import User

    config = get_google_auth_config()
    # data = request.get_json()
    try:
        token = request.json.get("token")
        if not token:
            return jsonify({"message": "Token missing"}), 400

        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), config["client_id"]
        )

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        email = idinfo.get("email")
        if not email:
            return jsonify({"message": "Email not provided by Google"}), 400

        user = User.objects(username=email).first()
        if not user:
            user = User(
                username=email, google_id=idinfo["sub"], role=config["default_role"]
            )
            user.save()

        jwt_token = jwt.encode(
            {
                "username": user.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                "role": user.role,
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return (
            jsonify(
                {
                    "token": (
                        jwt_token.decode("utf-8")
                        if isinstance(jwt_token, bytes)
                        else jwt_token
                    ),
                    "is_new_user": not user.password,  # Indicate if this is a first-time user
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"message": f"Invalid Google token: {str(e)}"}), 401


# Example protected route (you'll need a decorator for this - see below)
# @app.route('/protected')
# @token_required
# def protected():
#     return jsonify({'message': 'This is a protected route'})

# Example of a token_required decorator


# Auth Decorator
def token_required(f):
    """JWT token verification decorator"""

    @wraps(f)
    def decorated(*args, **kwargs):
        from .models import User

        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.objects(username=data["username"]).first()
            if not current_user:
                return jsonify({"message": "Invalid token - user not found"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            current_app.logger.error(f"Token verification error: {str(e)}")
            return jsonify({"message": "Token verification failed"}), 500

        return f(current_user, *args, **kwargs)

    return decorated

    # Example usage of the decorator in a route
    # from flask import Blueprint
    # api_bp = Blueprint("api", __name__)
    # @api_bp.route('/test')
    # @token_required
    # def test_route(current_user):
    #     return jsonify({"message": f"Hello, {current_user.username}!"})


# @some_blueprint.route("/protected")
# @token_required
# def protected_route(current_user):
#     return jsonify({
#         "message": f"Hello {current_user.username}",
#         "role": current_user.role
#     })
# if __name__ == '__main__':
#     app.run(debug=True)


def role_required(required_roles):
    """
    Decorator that checks if the user has the required role(s)
    Args:
        required_roles: string or list of strings representing allowed roles
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ensure we have a current_user (works with token_required)
            
            # Retrieve current_user from args
            current_user = None
            if args:
                current_user = args[0]
            
            if current_user is None:
                return jsonify({"error": "User not authenticated"}), 401

            # Convert single role string to list for uniform handling
            if isinstance(required_roles, str):
                allowed_roles = [required_roles]
            else:
                allowed_roles = required_roles
            # Check if user has any of the required roles
            if current_user.role not in allowed_roles:
                current_app.logger.warning(f"User {current_user.username} with role {current_user.role} attempted to access {request.path} requiring {allowed_roles}")
                return jsonify({"message": "Insufficient permissions"}), 403
            

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# # Example protected admin route
# @auth_bp.route("/admin-only")
# @token_required
# @role_required("admin")
# def admin_dashboard(current_user):
#     return jsonify(
#         {
#             "message": f"Welcome Admin {current_user.username}",
#             "admin_data": "Sensitive admin information",
#         }
#     )


# # Example route for multiple roles
# @auth_bp.route("/management")
# @token_required
# @role_required(["admin", "manager"])
# def management_dashboard(current_user):
#     return jsonify(
#         {
#             "message": f"Welcome {current_user.role.capitalize()} {current_user.username}",
#             "management_data": "Sensitive management information",
#         }
#     )
