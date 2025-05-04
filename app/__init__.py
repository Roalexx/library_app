from flask import Flask, Blueprint, request, jsonify
from app.models import db, User
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from config import Config


user_bp = Blueprint("user", __name__)
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    Swagger(app)  # ✅ Flasgger aktif!

    from app.routes.user import user_bp
    app.register_blueprint(user_bp)

    return app

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

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
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
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
