from flask import Blueprint, request, jsonify
from app.models import db, User
from werkzeug.security import generate_password_hash
from flasgger.utils import swag_from

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["POST"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Create a new user',
    'description': 'Creates a new user with username, email, and password.',
    'consumes': ['application/json'],
    'parameters': [
        {'name':'username', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Username'},
        {'name':'email', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'e-mail'},
        {'name':'password', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Password'}
    ],
    'responses': {
        201: {
            'description': 'User created successfully',
            'examples': {
                'application/json': {'message': 'User created'}
            }
        }
    }
})
def create_user():
    data = request.get_json()
    new_user = User(
        username=data["username"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"])
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
    'description': 'Updates the username, email or password of a user.',
    'parameters': [
        {'name':'username', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Username'},
        {'name':'email', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'e-mail'},
        {'name':'password', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Password'}
    ],
    'responses': {
        200: {
            'description': 'User updated successfully',
            'examples': {
                'application/json': {'message': 'User updated'}
            }
        }
    }
})
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    if "password" in data:
        user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"message": "User updated"})


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete a user',
    'description': 'Deletes a user by ID.',
    'parameters': [
        {'name':'user_id', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'User ID to delete'},        
    ],
    'responses': {
        200: {
            'description': 'User deleted successfully',
            'examples': {
                'application/json': {'message': 'User deleted'}
            }
        },
        404: {
            'description': 'User not found'
        }
    }
})
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
