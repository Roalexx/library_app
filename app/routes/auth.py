from flask import request, jsonify, Blueprint
from flasgger import swag_from
from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import generate_password_hash
from app.models import User, db
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Login User',
    'description': 'Login with username and password.',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User logged in successfully',
            'examples': {
                'application/json': {'user_token': '123456'}
            }
        },
        400: {'description': 'Missing username or password'},
        401: {'description': 'Bad username or password'}
    }
})
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'user_token': access_token}), 200


@auth_bp.route("/register", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Register a new user',
    'description': 'Registers a new user using username, email, and password.',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {
                'application/json': {'message': 'User registered'}
            }
        },
        400: {
            'description': 'Missing data',
            'examples': {
                'application/json': {'error': 'Eksik veri'}
            }
        }
    }
})
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Eksik veri"}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

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