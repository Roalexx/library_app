from flask import Blueprint, request, jsonify
from app.models import db, User
from werkzeug.security import generate_password_hash
from flasgger.utils import swag_from
from flask_jwt_extended import jwt_required, current_user

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["POST"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Create a new user',
    'description': 'Creates a new user with username, email, password, and optional is_admin flag.',
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
                    'password': {'type': 'string'},
                    'is_admin': {'type': 'boolean', 'default': False}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User created successfully',
            'examples': {
                'application/json': {'message': 'User created'}
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
def create_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    is_admin = data.get("is_admin", False) 

    if not username or not email or not password:
        return jsonify({"error": "Eksik veri"}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=is_admin
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


@user_bp.route("/users", methods=["GET"])
@swag_from({
    'tags': ['Users'],
    'summary': 'List all users',
    'description': 'Returns a list of all users.',
    'responses': {
        200: {
            'description': 'List of users',
            'examples': {
                'application/json': [
                    {"id": 1, "username": "elovate", "email": "elo@email.com"}
                ]
            }
        }
    }
})
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": user.id, "username": user.username, "email": user.email} for user in users
    ])


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Update a user',
    'security': [{'Bearer': []}],
    'description': 'Updates the username, email or password of a user.',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to update'
        },
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
                'required': ['username', 'email']
            }
        }
    ],
    'responses': {
        200: {'description': 'User updated successfully'},
        404: {'description': 'User not found'}
    }
})
@jwt_required()
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)

    password = data.get("password")
    if password:
        user.password_hash = generate_password_hash(password)

    db.session.commit()
    return jsonify({"message": "User updated"}), 200


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete a user',
    'security': [{'Bearer': []}],
    'description': 'Deletes a user by ID.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to delete'
        }
    ],
    'responses': {
        200: {'description': 'User deleted successfully'},
        404: {'description': 'User not found'}
    }
})
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200
