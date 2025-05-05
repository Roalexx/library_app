from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from config import Config
from flask_jwt_extended import JWTManager
from swagger_config import swagger_template


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    jwt = JWTManager(app)
    app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY
 
    db.init_app(app)
    migrate.init_app(app, db)
    Swagger(app, template=swagger_template)

    from app.models import User

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    from app.routes.books import books_bp
    from app.routes.user import user_bp
    from app.routes.auth import auth_bp    
    from app.routes.loan import loan_bp

    
    app.register_blueprint(books_bp)
    app.register_blueprint(user_bp)   
    app.register_blueprint(auth_bp)
    app.register_blueprint(loan_bp)

    return app
