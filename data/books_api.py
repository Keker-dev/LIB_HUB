import flask
from flask import Blueprint, jsonify, make_response, request, session, abort
from . import db_session
from .books import Book
from .comments import Comment
from .tags import Tag
from .users import User
from .pages import Page
from .auth import token_auth

blueprint = Blueprint(
    'books_api',
    __name__,
    template_folder='templates'
)
db_sess = None


@blueprint.route('/api/books')
@token_auth.login_required
def get_books():
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    books = db_sess.query(Book).all()
    return jsonify({'books': [item.to_dict() for item in books]})


@blueprint.route('/api/books/<book_name>', methods=['GET'])
def get_one_book(book_name):
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    return jsonify({'book': book.to_dict()})


@blueprint.route('/api/books', methods=['POST'])
@token_auth.login_required
def create_book():
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
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


@blueprint.route('/api/books/<book_name>/pages/<int:num>/comments', methods=['GET'])
@token_auth.login_required
def get_page_comments(book_name, num):
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    page = db_sess.query(Page).filter(Page.number == num, Page.book_id == book.id).first()
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    if not page:
        return make_response(jsonify({'error': 'The page was not found'}), 404)
    return jsonify({"comments": [item.to_dict() for item in page.comments]})


@blueprint.route('/api/books/<book_name>/pages/<int:num>/comments', methods=['POST'])
@token_auth.login_required
def create_page_comment(book_name, num):
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    page = db_sess.query(Page).filter(Page.number == num, Page.book_id == book.id).first()
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    if not page:
        return make_response(jsonify({'error': 'The page was not found'}), 404)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['text']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    comm = Comment(number=len(page.comments), text=request.json["text"], author_id=usr.id, page_id=page.id)
    db_sess.add(comm)
    db_sess.commit()
    return jsonify({"success": True, 'comment': comm.to_dict()})


@blueprint.route('/api/books/<book_name>/pages', methods=['POST'])
@token_auth.login_required
def create_page(book_name):
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book:
        return make_response(jsonify({'error': 'The book was not found'}), 404)
    if book.author_id != usr.id:
        return make_response(jsonify({'error': 'This book does not belong to you.'}), 403)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['name', 'text']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    page = Page(**request.json, number=len(book.pages), book_id=book.id)
    db_sess.add(page)
    db_sess.commit()
    return jsonify({"success": True, 'id': page.id, "name": page.name})


@blueprint.route('/api/tags', methods=['GET'])
def get_tags():
    return jsonify({"tags": [item.to_dict() for item in db_sess.query(Tag).all()]})