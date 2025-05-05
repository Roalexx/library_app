from flask import request, jsonify, Blueprint
from flasgger import swag_from
from flask_jwt_extended import create_access_token, jwt_required, current_user
from app import db
from app.models import User, Book, Loan
from datetime import datetime, timedelta

loan_bp = Blueprint("loan", __name__)

@loan_bp.route("/loans/creat", methods=["POST"])
@swag_from({
    'tags': ['Loans'],
    'summary': 'Create a new loan',
    'security': [{'Bearer': []}],
    'consumes': ['application/x-www-form-urlencoded'],
    'parameters': [
        {'name': 'username', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Username of borrower'},
        {'name': 'book_title', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Book title'},
        {'name': 'loan_date', 'in': 'formData', 'type': 'string', 'format': 'date-time', 'required': False, 'description': 'Loan date (optional)'},
        {'name': 'due_date', 'in': 'formData', 'type': 'string', 'format': 'date-time', 'required': False, 'description': 'Due date (optional)'}
    ],
    'responses': {
        201: {'description': 'Loan created'},
        400: {'description': 'Invalid data'},
        404: {'description': 'User or Book not found'}
    }
})
@jwt_required()
def create_loan():
    if not current_user.is_admin:
        return jsonify({"msg": "Only admins can perform this action"}), 403
    
    username = request.form.get("username")
    book_title = request.form.get("book_title")
    loan_date_str = request.form.get("loan_date")
    due_date_str = request.form.get("due_date")

    if not username or not book_title:
        return jsonify({"msg": "username and book_title are required"}), 400

    user = User.query.filter_by(username=username).first()
    book = Book.query.filter_by(title=book_title).first()

    if not user or not book:
        return jsonify({"msg": "User or Book not found"}), 404
    

    if book.available_copies <= 0:
        return jsonify({"msg": "No available copies of this book"}), 400

    try:
        loan_date = datetime.fromisoformat(loan_date_str) if loan_date_str else datetime.utcnow()
    except ValueError:
        return jsonify({"msg": "Invalid loan_date format"}), 400

    try:
        due_date = datetime.fromisoformat(due_date_str) if due_date_str else loan_date + timedelta(days=30)
    except ValueError:
        return jsonify({"msg": "Invalid due_date format"}), 400

    loan = Loan(
        user_id=user.id,
        book_id=book.id,
        loan_date=loan_date,
        due_date=due_date
    )

    book.available_copies -= 1

    db.session.add(loan)
    db.session.commit()
    return jsonify({"message": "Loan created"}), 201

@loan_bp.route("/loans/active", methods=["GET"])
@swag_from({
    'tags': ['Loans'],
    'summary': 'Get all active loans',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'List of all active loans',
            'examples': {
                'application/json': [
                    {'id': 1, 'user_id': '1', 'book_id': '1', 'loan_date': 'Wed, 04 Jun 2025 13:05:58 GMT', 'due_date': '2Mon, 05 May 2025 13:05:58 GMT'}
                ]
            }
        }
    }
})
@jwt_required()
def get_all_active_loans():
    loans = Loan.query.all()
    active_loans = []
    for loan in loans:
        if not loan.is_returned:
            active_loans.append(loan)
    return jsonify([
        {
            'loan_id': loan.id, 'user_id': loan.user_id, 'book_id': loan.book_id, 'loan_date':loan.loan_date, 'due_date': loan.due_date
        }
        for loan in active_loans
    ]),200

@loan_bp.route("/loans/deactive", methods=["GET"])
@swag_from({
    'tags': ['Loans'],
    'summary': 'Get all deactive loans',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'List of all deactive loans',
            'examples': {
                'application/json': [
                    {'id': 1, 'user_id': '1', 'book_id': '1', 'loan_date': 'Wed, 04 Jun 2025 13:05:58 GMT', 'due_date': '2Mon, 05 May 2025 13:05:58 GMT'}
                ]
            }
        }
    }
})
@jwt_required()
def get_all_deactive_loans():
    loans = Loan.query.filter_by(is_returned=True).all()
    return jsonify([
        {
            'loan_id': loan.id, 'user_id': loan.user_id, 'book_id': loan.book_id, 'loan_date':loan.loan_date, 'due_date': loan.due_date
        }
        for loan in loans
    ]),200

@loan_bp.route("/loans/deliver", methods=["POST"])
@swag_from({
    'tags': ['Loans'],
    'summary': 'Deliver a loan',
    'security': [{'Bearer': []}],
    'consumes': ['application/x-www-form-urlencoded'],
    'parameters': [
        {'name': 'loan_id', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'ID of loan'},
    ],
    'responses': {
        201: {'description': 'Book delivered successfully.'},
        400: {'description': 'Invalid data'},
        403: {'msg': 'Only admins can perform this action'}
    }

})
@jwt_required()
def deliver_loan():
    if not current_user.is_admin:
        return jsonify({"msg": "Only admins can perform this action"}), 403
    
    loan_id = request.form.get("loan_id")
    due_date = datetime.utcnow()
    loan = Loan.query.filter_by(id=loan_id)
    book = Book.query.filter_by(id=loan.book_id)

    book.available_copies += 1
    loan.is_returned = True
    
    return jsonify({'Book delivered successfully.'})