from data.db_session import create_session, global_init
from data.users import User
from data.books import Book
from data.pages import Page
import datetime
from forms.login import LoginForm
from forms.book import BookForm
from forms.page import PageForm
from forms.add_page import AddPageForm
from forms.register import RegisterForm
from forms.main_page import MainPageForm
from forms.profile import ProfileForm
from forms.add_book import AddBookForm
from flask import Flask
from flask import url_for, request, render_template, redirect, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'libhub_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
db_sess = None


@app.route("/", methods=["POST", "GET"])
def main_page():
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    usr_name, form = None, MainPageForm()
    if all(usr_data):
        usr_name = db_sess.query(User).filter(User.id == usr_data[0]).first().name
    if form.reg.data:
        return redirect(url_for("register_page"))
    if form.log.data:
        return redirect(url_for("login_page"))
    if form.profile.data and usr_name:
        return redirect(f"/profile/{usr_name}")
    if form.add_book.data:
        return redirect(url_for("add_book_page"))
    return render_template("main_page.html", title="LIBHUB", name=usr_name, form=form)


@app.route("/register", methods=["POST", "GET"])
def register_page():
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
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
        session["password"] = user.hashed_password
        return redirect(url_for("main_page"))
    elif all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/profile/<name>", methods=["POST", "GET"])
def profile_page(name):
    global db_sess
    form, usr = ProfileForm(), None
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    if form.submit.data and all(usr_data):
        session.pop("id")
        session.pop("email")
        session.pop("password")
        return redirect(url_for("main_page"))
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0]).first()
    return render_template('profile.html', title=f'Профиль {name}', form=form, name=name, usr=usr)


@app.route("/login", methods=["POST", "GET"])
def login_page():
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    form = LoginForm()
    if form.validate_on_submit() and not all(usr_data):
        user = db_sess.query(User).filter(
            User.email == form.name.data if "@" in form.name.data else User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            session["id"] = user.id
            session["email"] = user.email
            session["password"] = user.hashed_password
        else:
            return render_template('login.html', title='Вход', form=form,
                                   message="Неправильный пароль или логин")
        return redirect(url_for("main_page"))
    elif all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('login.html', title='Вход', form=form)


@app.route("/add_book", methods=["POST", "GET"])
def add_book_page():
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    form = AddBookForm()
    if form.validate_on_submit() and all(usr_data):
        user = db_sess.query(User).filter(User.id == usr_data[0]).first()
        if db_sess.query(Book).filter(Book.name == form.name.data).first():
            return render_template('add_book.html', title='Добавление книги', form=form,
                                   message="Книга с таким названием уже есть")
        book = Book(name=form.name.data, author_id=user.id)
        db_sess.add(book)
        db_sess.commit()
        return redirect(f"/book/{form.name.data}")
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('add_book.html', title='Добавление книги', form=form)


@app.route("/book/<book_name>/add_page", methods=["POST", "GET"])
def add_page_page(book_name):
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    form = AddPageForm()
    if form.validate_on_submit() and all(usr_data):
        book = db_sess.query(Book).filter(Book.author_id == usr_data[0], Book.name == book_name).first()
        page = Page(name=form.name.data, text=form.text.data, number=len(book.pages))
        page.book_id = book.id
        db_sess.add(page)
        db_sess.commit()
        return redirect(f"/book/{book_name}")
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('add_page.html', title='Добавление главы', form=form)


@app.route("/book/<book_name>", methods=["POST", "GET"])
def book_page(book_name):
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    form, usr = BookForm(), None
    if form.add_page.data and all(usr_data):
        return redirect(f"/book/{book_name}/add_page")
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if form.read.data:
        return redirect(f"/book/{book_name}/page/0")
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0]).first()
    prms = {
        "form": form,
        "title": f'Книга {book_name}',
        "book": book,
        "usr": usr,
    }
    return render_template('book.html', **prms)


@app.route("/book/<book_name>/page/<page_num>", methods=["POST", "GET"])
def book_page_page(book_name, page_num):
    global db_sess
    form, page_num = PageForm(), int(page_num)
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if not book or not (0 <= page_num < len(book.pages)):
        return redirect(url_for("main_page"))
    if form.next.data:
        return redirect(f"/book/{book_name}/page/{(page_num + 1) % len(book.pages)}")
    if form.prev.data:
        return redirect(f"/book/{book_name}/page/{page_num - 1 if page_num - 1 >= 0 else 0}")
    prms = {
        "title": f'Книга {book_name}',
        "book": book,
        "page": [pg for pg in book.pages if pg.number == page_num][0],
        "form": form,
    }
    return render_template('page.html', **prms)


def main():
    global db_sess
    global_init("db/main.db")
    db_sess = create_session()
    app.run()


if __name__ == '__main__':
    main()
