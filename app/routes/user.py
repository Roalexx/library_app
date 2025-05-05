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
    'description': 'Creates a new user with username, email, and password.',
    'consumes': ['application/x-www-form-urlencoded'],
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
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Eksik veri"}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
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


@user_bp.route("/users", methods=["PUT"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Update a user',
    'security': [{'Bearer': []}],
    'description': 'Updates the username, email or password of a user.',
    'consumes': ['application/x-www-form-urlencoded'],
    'parameters': [
        {'name':'user_id', 'in': 'formData', 'type': 'integer', 'required': True, 'description': 'User ID'},
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
@jwt_required()
def update_user():
    user_id = request.form.get("user_id", type=int)
    user = User.query.get_or_404(user_id)

    user.username = request.form.get("username")
    user.email = request.form.get("email")

    password = request.form.get("password")
    if password:
        user.password_hash = generate_password_hash(password)

    db.session.commit()
    return jsonify({"message": "User updated"}), 200


@user_bp.route("/users", methods=["DELETE"])
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete a user',
    'security': [{'Bearer': []}],
    'description': 'Deletes a user by ID.',
    'consumes': ['application/x-www-form-urlencoded'],
    'parameters': [
        {'name':'user_id', 'in': 'formData', 'type': 'integer', 'required': True, 'description': 'User ID to delete'},        
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
@jwt_required()
def delete_user():
    user_id = request.form.get("user_id", type=int)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
