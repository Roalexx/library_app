from flask import request, jsonify, Blueprint
from flasgger import swag_from
from flask_jwt_extended import create_access_token, jwt_required, current_user
from app.models import User
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'summary': 'login User',
    'description': 'login with username and password.',
    'consumes': ['application/x-www-form-urlencoded'],
    'parameters': [
        {'name':'username', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Username'},
        {'name':'password', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Password'}
    ],
    'responses': {
        201: {
            'description': 'User logged in successfully',
            'examples': {
                'application/json': {'message': 'user_token : 123456'}
            }
        }
    }
})
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'user_token': access_token}), 200

@auth_bp.route("/who_am_i", methods=["GET"])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Get current user info',
    'security': [{'Bearer': []}], 
    'responses': {
        200: {
            'description': 'Current user info',
            'examples': {
                'application/json': {
                    "id": 1,
                    "username": "elovate",
                    "email": "elovate@example.com"
                }
            }
        },
        401: {
            'description': 'Unauthorized - Missing or invalid token',
            'examples': {
                'application/json': {
                    "msg": "Missing Authorization Header"
                }
            }
        }
    }
})
@jwt_required()
def who_am_i():
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }), 200