from data.session_db import db_sess
from socket import gethostname
from data import books_api, users_api
from sqlalchemy import desc, func, literal
from data.users import User
from data.books import Book
from data.pages import Page
from data.tokens import Token
from data.comments import Comment
from data.tags import Tag
import datetime, base64
from forms.login import LoginForm
from forms.book import BookForm
from forms.page import PageForm
from forms.add_page import AddPageForm, decode_bytes
from forms.register import RegisterForm
from forms.main_page import MainPageForm
from forms.profile import ProfileForm
from forms.add_book import AddBookForm
from forms.edit_book import EditBookForm
from forms.settings import SettingsForm
from forms.reader import ReaderForm
from forms.author_cab import AuthorForm
from flask import url_for, request, render_template, redirect, session, jsonify, make_response, abort, Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'libhub_secret_key'
app.register_blueprint(books_api.blueprint)
app.register_blueprint(users_api.blueprint)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)


@app.errorhandler(404)
def not_found(error):
    err = {"name": str(error)[:str(error).index(":")],
           "text": "Упс... Страница не найдена."}
    return render_template("error.html", error=err)


@app.errorhandler(400)
def bad_request(error):
    err = {"name": str(error)[:str(error).index(":")],
           "text": "Упс... Сервер не понял ваш запрос."}
    return render_template("error.html", error=err)


@app.errorhandler(403)
def block_request(error):
    err = {"name": str(error)[:str(error).index(":")],
           "text": "Сервер вас заблокировал за подозрительную активность."}
    return render_template("error.html", error=err)


@app.route("/error/<error>")
def error_page(error):
    err = {"name": error[:error.index("|")],
           "text": error[error.index("|") + 1:]}
    return render_template("error.html", error=err)


@app.route("/", methods=["POST", "GET"])
def main_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = MainPageForm(), None
    prms = {"title": "LIBHUB", "usr": None, "form": form, "message": None, "search_results": [],
            "popular": db_sess.query(Book).order_by(Book.views).limit(16).all()}
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            session.pop("id")
            session.pop("email")
            session.pop("name")
            return redirect(url_for("main_page"))
        else:
            prms["usr"] = usr
    if form.reg.data:
        return redirect(url_for("register_page"))
    if form.log.data:
        return redirect(url_for("login_page"))
    if form.profile.data and usr:
        return redirect(url_for("profile_page", name=usr.name))
    if form.settings.data and usr:
        return redirect(url_for("settings_page"))
    if form.write_cab.data:
        return redirect(url_for("author_cabinet_page"))
    if form.read_cab.data:
        return redirect(url_for("reader_cabinet_page"))
    if request.method == "POST" and request.form["searchbtn"]:
        books = db_sess.query(Book).all()
        books = [i for i in books if form.search.data.lower() in i.name.lower()]
        if books:
            prms["search_results"] = books
        else:
            prms["message"] = "Ничего не найдено."
    prms["form"] = form
    return render_template("main_page.html", **prms)


@app.route("/register", methods=["POST", "GET"])
def register_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter((User.email == form.email.data) | (User.name == form.name.data)).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        session["id"] = user.id
        session["email"] = user.email
        session["name"] = user.name
        return redirect(url_for("main_page"))
    elif all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/profile/<name>", methods=["POST", "GET"])
def profile_page(name):
    form, usr, ch_usr = ProfileForm(), None, db_sess.query(User).filter(User.name == name).first()
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    if not ch_usr:
        return redirect(url_for("error_page", error="993|К сожалению этот пользователь удалён."))
    if form.submit.data and all(usr_data):
        return redirect(url_for("settings_page"))
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            session.pop("id")
            session.pop("email")
            session.pop("name")
            return redirect(url_for("main_page"))
    if form.like.data and usr:
        if usr.id not in ch_usr.likes:
            ch_usr.likes = ch_usr.likes + [usr.id]
        else:
            lks = ch_usr.likes.copy()
            lks.remove(usr.id)
            ch_usr.likes = lks
        ch_usr.likes_count = len(ch_usr.likes)
    if form.favorite.data and usr:
        if ch_usr.id not in usr.favorite_authors:
            usr.favorite_authors = usr.favorite_authors + [ch_usr.id]
        else:
            lks = usr.favorite_authors.copy()
            lks.remove(ch_usr.id)
            usr.favorite_authors = lks
    db_sess.commit()
    return render_template('profile.html', title=f'Профиль {name}', form=form, ch_usr=ch_usr, usr=usr)


@app.route("/login", methods=["POST", "GET"])
def login_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form = LoginForm()
    if form.validate_on_submit() and not all(usr_data):
        user = db_sess.query(User).filter(
            User.email == form.name.data if "@" in form.name.data else User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            session["id"] = user.id
            session["email"] = user.email
            session["name"] = user.name
        else:
            return render_template('login.html', title='Вход', form=form,
                                   message="Неправильный пароль или логин")
        return redirect(url_for("main_page"))
    elif all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('login.html', title='Вход', form=form)


@app.route("/add_book", methods=["POST", "GET"])
def add_book_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    tags = db_sess.query(Tag).all()
    form, user = AddBookForm(), None
    if form.validate_on_submit() and all(usr_data):
        user = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                          User.name == usr_data[2]).first()
        if not user:
            return redirect(url_for("main_page"))
        if db_sess.query(Book).filter(Book.name == form.name.data).first():
            return render_template('add_book.html', title='Добавление книги', form=form,
                                   message="Книга с таким названием уже есть", usr=user)
        tags_id = []
        for i in request.values:
            if "tag_" in i:
                tags_id.append(int(i[4:]))
        encoded_photo = ""
        if form.photo.data:
            photo = form.photo.data
            encoded_photo = base64.b64encode(photo.read())
            encoded_photo = encoded_photo.decode("utf-8")
        book = Book(name=form.name.data, author_id=user.id, tags=sorted(tags_id), image=encoded_photo,
                    price=form.price.data, about=form.about.data)
        db_sess.add(book)

        subs = db_sess.query(User).filter(User.favorite_authors.contains(book.author_id)).all()
        for sub in subs:
            nfs = sub.notifs.copy()
            nfs["read"] = nfs["read"] + [
                {"type": "new_book", "book": book.name,
                 "text": f'Вышла новая книга "{book.name}" от {book.author.name}'}]
            sub.notifs = nfs
        db_sess.commit()
        return redirect(url_for("book_page", book_name=form.name.data))
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('add_book.html', title='Добавление книги', form=form, tags=tags, usr=user)


@app.route("/book/<book_name>/edit", methods=["POST", "GET"])
def edit_book_page(book_name):
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    tags = db_sess.query(Tag).all()
    form, user = EditBookForm(), None
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book:
        abort(404)
    if form.validate_on_submit() and all(usr_data):
        user = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                          User.name == usr_data[2]).first()
        if not user:
            return redirect(url_for("main_page"))
        tags_id = []
        for i in request.values:
            if "tag_" in i:
                tags_id.append(int(i[4:]))
        encoded_photo = ""
        if form.photo.data:
            photo = form.photo.data
            encoded_photo = base64.b64encode(photo.read())
            encoded_photo = encoded_photo.decode("utf-8")
        if encoded_photo:
            book.image = encoded_photo
        if db_sess.query(Book).filter(Book.name == form.name.data).first():
            form.name.errors = tuple([*form.name.errors, "Это имя занято."])
        else:
            book.name = form.name.data
        book.about = form.about.data
        book.price = form.price.data
        db_sess.commit()
        return redirect(url_for("book_page", book_name=form.name.data))
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    form.name.data = book.name
    form.about.data = book.about
    form.price.data = book.price
    return render_template('edit_book.html', title='Добавление книги', form=form, tags=tags,
                           usr=user, book=book)


@app.route("/book/<book_name>/add_page", methods=["POST", "GET"])
def add_page_page(book_name):
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = AddPageForm(), None
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
    if form.validate_on_submit() and usr:
        book = db_sess.query(Book).filter(Book.author_id == usr_data[0], Book.name == book_name).first()
        text = form.text.data if form.text.data else decode_bytes(form.file.data.read())
        page = Page(name=form.name.data, text=text, number=len(book.pages))
        page.book_id = book.id
        db_sess.add(page)
        subs = db_sess.query(User).filter(User.favorite_books.contains(book.id)).all()
        for sub in subs:
            nfs = sub.notifs.copy()
            nfs["read"] = nfs["read"] + [{"type": "new_page", "book": book.name, "page": page.number,
                                          "text": f'Вышла новая глава "{page.name}" в "{book.name}"'}]
            sub.notifs = nfs
        db_sess.commit()
        return redirect(url_for("book_page", book_name=book_name))
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('add_page.html', title='Добавление главы', form=form, usr=usr)


@app.route("/book/<book_name>", methods=["POST", "GET"])
def book_page(book_name):
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = BookForm(), None
    if form.add_page.data and all(usr_data):
        return redirect(url_for("add_page_page", book_name=book_name))
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book:
        return redirect(url_for("error_page", error="228|К сожалению такой книги нет."))
    if form.read.data:
        return redirect(url_for("book_page_page", book_name=book_name, page_num=0))
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
        if usr.id not in book.views and usr.id != book.author_id:
            book.views = book.views + [usr.id]
            book.views_count = len(book.views)
            if book.views_count > 10 and book.views_count % 100 == 0:
                nfs = book.author.notifs.copy()
                nfs["write"] = nfs["write"] + [{"type": "up_views", "book": book.name,
                                                "text": f'Книга "{book.name}" достигла {book.views_count} просмотров!'}]
                book.author.notifs = nfs
        if book.id not in usr.last_books and book.author_id != usr.id:
            if len(usr.last_books) < usr.settings["len-last-seen"]:
                usr.last_books = usr.last_books + [book.id]
            else:
                lst = usr.last_books.copy()
                lst.pop(0)
                usr.last_books = lst + [book.id]
    if form.author.data:
        if book.author:
            return redirect(url_for("profile_page", name=book.author.name))
        else:
            return redirect(url_for("error_page", error="993|К сожалению этот пользователь удалён."))
    if form.favorite.data and usr:
        if book.id not in usr.favorite_books:
            usr.favorite_books = usr.favorite_books + [book.id]
        else:
            bks = usr.favorite_books.copy()
            bks.remove(book.id)
            usr.favorite_books = bks
    form.author.label.text = f"Автор: {book.author.name if book.author else ''}"
    prms = {
        "form": form,
        "title": f'Книга {book_name}',
        "book": book,
        "usr": usr,
        "tags": db_sess.query(Tag).filter(Tag.id.in_(book.tags)).all(),
    }
    db_sess.commit()
    return render_template('book.html', **prms)


@app.route("/book/<book_name>/page/<page_num>", methods=["POST", "GET"])
def book_page_page(book_name, page_num):
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, page_num, usr = PageForm(), int(page_num), None
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
    if not book:
        return redirect(url_for("main_page"))
    elif not (0 <= page_num < len(book.pages)):
        return redirect(url_for("book_page", book_name=book_name))
    page = [pg for pg in book.pages if pg.number == page_num][0]
    if form.next.data:
        return redirect(url_for("book_page_page", book_name=book_name,
                                page_num=page_num + 1 if page_num + 1 < len(book.pages) else page_num))
    if form.prev.data:
        return redirect(url_for("book_page_page", book_name=book_name,
                                page_num=page_num - 1 if page_num - 1 >= 0 else 0))
    if form.comm_sub.data:
        comm = Comment(text=form.comm_field.data, author_id=usr_data[0], page_id=page.id, number=len(page.comments))
        nfs = book.author.notifs.copy()
        nfs["write"] = nfs["write"] + [{"type": "new_comm", "book": book.name, "page": page.number,
                                        "text": f'Новый комментарий к книге "{book.name}" главе {page.name}!'}]
        book.author.notifs = nfs
        db_sess.add(comm)
        db_sess.commit()
    if form.like.data and usr:
        com = db_sess.query(Comment).get(int(form.like.data))
        if usr.id not in com.likes:
            com.likes = com.likes + [usr.id]
        else:
            lks = com.likes.copy()
            lks.remove(usr.id)
            com.likes = lks
        com.likes_count = len(com.likes)
        if com.likes_count > 9 and com.likes_count % 10 == 0:
            nfs = com.author.notifs.copy()
            nfs["read"] = (nfs["read"] +
                           [{"type": "com_like", "book": book.name, "page": page.number,
                             "text": 'Ваш комментарий к главе "{pg}" книги "{bk}" достиг {lk} лайков!'.format(
                                 pg=page.name, bk=book.name, lk=com.likes_count)}])
            com.author.notifs = nfs
    prms = {
        "title": f'Книга {book_name}',
        "book": book,
        "page": page,
        "form": form,
        "usr": usr,
    }
    return render_template('page.html', **prms)


@app.route("/settings", methods=["POST", "GET"])
def settings_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = SettingsForm(), None
    form.tabs_class.default = session.get("setts_tabs_id", "1")
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
    prms = {
        "title": f'Настройки',
        "form": form,
        "usr": usr,
    }
    setts = usr.settings.copy()
    if form.logout.data:
        session.pop("id")
        session.pop("email")
        session.pop("name")
        return redirect(url_for("main_page"))
    if form.del_acc.data:
        session.pop("id")
        session.pop("email")
        session.pop("name")
        db_sess.delete(usr)
        db_sess.commit()
        return redirect(url_for("main_page"))
    if form.change_name.data and form.change_name.data != usr.name:
        if db_sess.query(User).filter(User.name == form.change_name.data).first():
            form.change_name.errors = tuple([*form.change_name.errors, "Это имя занято."])
        else:
            usr.name = form.change_name.data
    if form.change_pass.data:
        usr.set_password(form.change_pass.data)
    if form.change_about.data:
        usr.about = form.change_about.data
    if form.change_about.data:
        usr.about = form.change_about.data
    if form.font.data:
        setts["font"] = form.font.data
    if form.font_color.data:
        setts["font-color"] = form.font_color.data
    if form.font_size.data:
        setts["font-size"] = form.font_size.data
    if form.ignore.data:
        setts["ignore"] = form.ignore.data
    if form.check_books.data:
        setts["len-last-seen"] = form.check_books.data
    if form.del_history.data:
        usr.last_books = []
    if form.add_token.data:
        if len(usr.tokens) > 10:
            prms["message"] = "Максимум 10 токенов!"
        else:
            token = Token(user_id=usr.id)
            token.get_token()
            db_sess.add(token)
    if form.validate_on_submit():
        for i in request.form.keys():
            if "rem_token_" in i:
                token = db_sess.query(Token).get(i[10:])
                if token:
                    db_sess.delete(token)
    usr.settings = setts
    db_sess.commit()
    form.change_name.data = usr.name
    form.change_about.data = usr.about
    form.font_color.data = usr.settings["font-color"]
    form.font_size.data = usr.settings["font-size"]
    form.font.data = usr.settings["font"]
    form.ignore.data = usr.settings["ignore"]
    form.check_books.data = usr.settings["len-last-seen"]
    session["setts_tabs_id"] = form.tabs_class.data
    return render_template('settings.html', **prms)


@app.route("/reader", methods=["POST", "GET"])
def reader_cabinet_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = ReaderForm(), None
    form.tabs_class.default = session.get("reader_tabs_id", "1")
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
    if form.validate_on_submit():
        for i in request.form.keys():
            if "rem_fav_auth_" in i:
                fav_auths = usr.favorite_authors.copy()
                fav_auths.remove(int(i[13:]))
                usr.favorite_authors = fav_auths
            if "rem_fav_book_" in i:
                fav_books = usr.favorite_books.copy()
                fav_books.remove(int(i[13:]))
                usr.favorite_books = fav_books
            if "rem_ntf_" in i:
                ntf = usr.notifs["read"][int(i[8:]) - 1]
                ntfs = usr.notifs.copy()
                ntfs["read"] = ntfs["read"].copy()
                ntfs["read"].pop(int(i[8:]) - 1)
                usr.notifs = ntfs
                if ntf["type"] == "new_page":
                    return redirect(url_for("book_page_page", book_name=ntf["book"], page_num=ntf["page"]))
                if ntf["type"] == "com_like":
                    return redirect(url_for("book_page_page", book_name=ntf["book"], page_num=ntf["page"]))
                if ntf["type"] == "new_book":
                    return redirect(url_for("book_page", book_name=ntf["book"]))
    prms = {
        "title": f'Кабинет читателя',
        "form": form,
        "usr": usr,
        "last_books": db_sess.query(Book).filter(Book.id.in_(usr.last_books)).all()[::-1],
        "fav_auths": db_sess.query(User).filter(User.id.in_(usr.favorite_authors)).all(),
        "fav_books": db_sess.query(Book).filter(Book.id.in_(usr.favorite_books)).all(),
    }
    session["reader_tabs_id"] = form.tabs_class.data
    db_sess.commit()
    return render_template('reader.html', **prms)


@app.route("/author", methods=["POST", "GET"])
def author_cabinet_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = AuthorForm(), None
    form.tabs_class.default = session.get("author_tabs_id", "1")
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
    if form.add_book.data:
        return redirect(url_for("add_book_page"))
    if form.validate_on_submit():
        for i in request.form.keys():
            if "rem_book_" in i:
                book = db_sess.get(Book, int(i[9:]))
                if not book:
                    continue
                for pg in book.pages:
                    for comm in pg.comments:
                        db_sess.delete(comm)
                    db_sess.delete(pg)
                db_sess.delete(book)
            if "edit_book_" in i:
                book = db_sess.get(Book, int(i[10:]))
                if not book:
                    continue
                return redirect(url_for("edit_book_page", book_name=book.name))
            if "rem_ntf_" in i:
                ntf = usr.notifs["write"][int(i[8:]) - 1]
                ntfs = usr.notifs.copy()
                ntfs["write"] = ntfs["write"].copy()
                ntfs["write"].pop(int(i[8:]) - 1)
                usr.notifs = ntfs
                if ntf["type"] == "new_comm":
                    return redirect(url_for("book_page_page", book_name=ntf["book"], page_num=ntf["page"]))
                if ntf["type"] == "up_views":
                    return redirect(url_for("book_page", book_name=ntf["book"]))
    prms = {
        "title": f'Кабинет читателя',
        "form": form,
        "usr": usr,
    }
    session["author_tabs_id"] = form.tabs_class.data
    db_sess.commit()
    return render_template('author_cab.html', **prms)


def main():
    if not db_sess.query(Tag).all():
        tags = [['Фантастика', 'Миры будущего с чудесами технологий и неизведанными галактиками.'],
                ['Приключения', 'Захватывающие путешествия главных героев, полные неожиданных встреч и испытаний.'],
                ['Романтика', 'Истории о любви, страсти и сложных отношениях, пробуждающие чувства.'],
                ['Ужасы', 'Темные и страшные сюжеты, погружающие в атмосферу неведомого и пугающего.'],
                ['Триллер',
                 'Напряженные сюжеты с интригующими поворотами, которые держат в напряжении до последней страницы.'],
                ['Детская литература',
                 'Яркие и увлекательные рассказы, которые развлекают и обучают маленьких читателей.'],
                ['Популярная психология', 'Книги, помогающие разобраться в себе и улучшить качество жизни.'],
                ['Исторический роман', 'Погружение в эпохи прошлого через призму вымышленных и реальных событий.'],
                ['Научная фантастика', 'Исследование возможных научных достижений и их влияния на человечество.'],
                ['Фэнтези', 'Очаровательные миры с магией, мифическими существами и эпическими квестами.'],
                ['Автобиография', 'Жизненные истории известных личностей, вдохновляющие на изменения в своей жизни.'],
                ['Детектив', 'Разгадывание загадок и расследование преступлений с хитроумными детективами.'],
                ['Современная проза', 'Портреты повседневной жизни и драмы, отражающие реалии современности.'],
                ['Поэзия', 'Стихотворные строки, передающие глубокие эмоции и чувства через метафоры.'],
                ['Сатира', 'Умные, ироничные произведения, высмеивающие общественные недостатки и пороки.'],
                ['Философия', 'Глубокие размышления о жизни, смысле существования и человеческой природе.'],
                ['Кулинария', 'Рецепты и истории, вдохновляющие готовить и открывать новые вкусы.'],
                ['Художественная литература',
                 'Классические и современные произведения, раскрывающие человеческие переживания.'],
                ['Криминал', 'Следствие, преступления и моральные дилеммы, о которых стоит задуматься.']]
        for tag in tags:
            db_sess.add(Tag(name=tag[0], about=tag[1]))
        db_sess.commit()
    if 'liveconsole' not in gethostname():
        app.run()


if __name__ == '__main__':
    main()
