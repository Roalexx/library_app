from flask import Blueprint, request, jsonify
from app.models import db, User
from werkzeug.security import generate_password_hash

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["POST"])
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
def list_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email
        } for u in users
    ])
