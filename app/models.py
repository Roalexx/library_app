from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db 

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    loans = db.relationship('Loan', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username}>"

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    available_copies = db.Column(db.Integer, nullable=False)

    loans = db.relationship('Loan', back_populates='book', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Book {self.title}>"

class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    is_returned = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='loans')
    book = db.relationship('Book', back_populates='loans')

    def __repr__(self):
        return f"<Loan {self.user_id} - {self.book_id}>"
