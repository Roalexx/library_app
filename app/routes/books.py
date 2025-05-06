from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.models import db, Book

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['POST'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Add a new book',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'author': {'type': 'string'},
                    'total_copies': {'type': 'integer'}
                },
                'required': ['title', 'author', 'total_copies']
            }
        }
    ],
    'responses': {
        201: {'description': 'Book successfully added'},
        400: {'description': 'Missing or invalid data'}
    }
})
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    total_copies = data.get('total_copies')

    if not title or not author or total_copies is None:
        return jsonify({'error': 'Eksik veri'}), 400

    book = Book(title=title, author=author, total_copies=total_copies, available_copies=total_copies)
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Kitap eklendi', 'book_id': book.id}), 201


@books_bp.route('/books', methods=['GET'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Get all books',
    'responses': {
        200: {
            'description': 'List of all books',
            'examples': {
                'application/json': [
                    {'id': 1, 'title': '1984', 'author': 'George Orwell', 'total_copies': 5, 'available_copies': 5}
                ]
            }
        }
    }
})
def get_all_books():
    books = Book.query.all()
    return jsonify([
        {
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'total_copies': b.total_copies,
            'available_copies': b.available_copies
        }
        for b in books
    ]), 200


@books_bp.route('/books/<int:book_id>', methods=['GET'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Get a book by ID',
    'parameters': [
        {'name': 'book_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'Book ID'}
    ],
    'responses': {
        200: {'description': 'Book found'},
        404: {'description': 'Book not found'}
    }
})
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Kitap bulunamadı'}), 404

    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'total_copies': book.total_copies,
        'available_copies': book.available_copies
    }), 200


@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Delete a book by ID',
    'parameters': [
        {'name': 'book_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': 'Book ID to delete'}
    ],
    'responses': {
        200: {'description': 'Book deleted successfully'},
        404: {'description': 'Book not found'}
    }
})
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Kitap bulunamadı'}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Kitap silindi'}), 200


@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Update a book by ID',
    'consumes': ['application/json'],
    'parameters': [
        {'name': 'book_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'author': {'type': 'string'},
                    'total_copies': {'type': 'integer'},
                    'available_copies': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Book updated'},
        404: {'description': 'Book not found'}
    }
})
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Kitap bulunamadı'}), 404

    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.total_copies = data.get('total_copies', book.total_copies)
    book.available_copies = data.get('available_copies', book.available_copies)

    db.session.commit()
    return jsonify({'message': 'Kitap güncellendi'}), 200
