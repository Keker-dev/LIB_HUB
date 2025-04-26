import flask
from flask import Blueprint, jsonify, make_response, request, session, abort
from . import db_session
from .books import Book
from .tags import Tag
from .users import User

blueprint = Blueprint(
    'books_api',
    __name__,
    template_folder='templates'
)
db_sess = None


@blueprint.route('/api/books')
def get_books():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                     User.name == usr_data[2]).first()
    if not usr or not all(usr_data):
        return make_response(jsonify({'error': 'You are not registered.'}), 403)
    books = db_sess.query(Book).all()
    return jsonify({'books': [item.to_dict() for item in books]})


@blueprint.route('/api/books/<book_name>', methods=['GET'])
def get_one_book(book_name):
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    return jsonify({'book': book.to_dict()})


@blueprint.route('/api/books', methods=['POST'])
def create_book():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                     User.name == usr_data[2]).first()
    if not usr or not all(usr_data):
        return make_response(jsonify({'error': 'You are not registered.'}), 403)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['name', 'about', 'tags']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    if not all([db_sess.query(Tag).get(tag_id) for tag_id in request.json["tags"]]):
        return make_response(jsonify({'error': 'Bad tags'}), 400)
    book = Book(**request.json, author_id=usr.id)
    db_sess.add(book)
    db_sess.commit()
    return jsonify({"success": True, 'id': book.id, "name": book.name})


@blueprint.route('/api/books/<book_name>/pages', methods=['GET'])
def get_pages(book_name):
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({"pages": [item.to_dict() for item in book.pages]})


@blueprint.route('/api/books/<book_name>/pages/<int:num>', methods=['GET'])
def get_page(book_name, num):
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    page = [pg for pg in book.pages if pg.number == num]
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    if not page:
        return make_response(jsonify({'error': 'The page was not found'}), 404)
    return jsonify({"page": page[0].to_dict()})


@blueprint.route('/api/books/<book_name>/pages', methods=['POST'])
def create_page(book_name):
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                     User.name == usr_data[2]).first()
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not usr or not all(usr_data):
        return make_response(jsonify({'error': 'You are not registered.'}), 403)
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    if book.author_id != usr.id:
        return make_response(jsonify({'error': 'This book does not belong to you.'}), 403)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['name', 'text']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    if not all([db_sess.query(Tag).get(tag_id) for tag_id in request.json["tags"]]):
        return make_response(jsonify({'error': 'Bad tags'}), 400)
    page = Page(**request.json, number=len(book.pages), book_id=book.id)
    db_sess.add(page)
    db_sess.commit()
    return jsonify({"success": True, 'id': page.id, "name": page.name})
