from data.db_session import create_session, global_init
from data.users import User
from data.books import Book
from data.pages import Page
from data.comments import Comment
from data.tags import Tag
import datetime
from json import dumps, loads
from forms.login import LoginForm
from forms.book import BookForm
from forms.page import PageForm
from forms.add_page import AddPageForm
from forms.register import RegisterForm
from forms.main_page import MainPageForm
from forms.profile import ProfileForm
from forms.add_book import AddBookForm
from forms.settings import SettingsForm
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
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = MainPageForm(), None
    prms = {"title": "LIBHUB", "usr": None, "setts": None, "form": form, "message": None, "search_results": []}
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
            prms["setts"] = loads(usr.settings)
    if form.reg.data:
        return redirect(url_for("register_page"))
    if form.log.data:
        return redirect(url_for("login_page"))
    if form.profile.data and usr:
        return redirect(url_for("profile_page", name=usr.name))
    if form.settings.data and usr:
        return redirect(url_for("settings_page"))
    if form.add_book.data:
        return redirect(url_for("add_book_page"))
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
    global db_sess
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
    global db_sess
    form, usr, ch_usr, setts = ProfileForm(), None, db_sess.query(User).filter(User.name == name).first(), None
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    if form.submit.data and all(usr_data):
        return redirect(url_for("settings_page"))
        session.pop("id")
        session.pop("email")
        session.pop("name")
        return redirect(url_for("main_page"))
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            session.pop("id")
            session.pop("email")
            session.pop("name")
            return redirect(url_for("main_page"))
        else:
            setts = loads(usr.settings)
    return render_template('profile.html', title=f'Профиль {name}', form=form, ch_usr=ch_usr,
                           usr=usr, setts=setts)


@app.route("/login", methods=["POST", "GET"])
def login_page():
    global db_sess
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
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    tags = db_sess.query(Tag).all()
    form, setts, user = AddBookForm(), None, None
    if form.validate_on_submit() and all(usr_data):
        user = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                          User.name == usr_data[2]).first()
        if not user:
            return redirect(url_for("main_page"))
        setts = loads(user.settings)
        if db_sess.query(Book).filter(Book.name == form.name.data).first():
            return render_template('add_book.html', title='Добавление книги', form=form,
                                   message="Книга с таким названием уже есть", usr=user, setts=setts)
        tags_id = []
        for i in request.values:
            if "tag_" in i:
                tags_id.append(int(i[4:]))
        book = Book(name=form.name.data, author_id=user.id, tags=str(sorted(tags_id)))
        db_sess.add(book)
        db_sess.commit()
        return redirect(url_for("book_page", book_name=form.name.data))
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('add_book.html', title='Добавление книги', form=form, tags=tags,
                           usr=user, setts=setts)


@app.route("/book/<book_name>/add_page", methods=["POST", "GET"])
def add_page_page(book_name):
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr, setts = AddPageForm(), None, None
    if form.validate_on_submit() and all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
        setts = loads(usr.settings)
        book = db_sess.query(Book).filter(Book.author_id == usr_data[0], Book.name == book_name).first()
        page = Page(name=form.name.data, text=form.text.data, number=len(book.pages))
        page.book_id = book.id
        db_sess.add(page)
        db_sess.commit()
        return redirect(url_for("book_page", book_name=book_name))
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    return render_template('add_page.html', title='Добавление главы', form=form, usr=usr, setts=setts)


@app.route("/book/<book_name>", methods=["POST", "GET"])
def book_page(book_name):
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = BookForm(), None
    if form.add_page.data and all(usr_data):
        return redirect(url_for("add_page_page", book_name=book_name))
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if form.read.data:
        return redirect(url_for("book_page_page", book_name=book_name, page_num=0))
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            session.pop("id")
            session.pop("email")
            return redirect(url_for("main_page"))
    prms = {
        "form": form,
        "title": f'Книга {book_name}',
        "book": book,
        "usr": usr,
    }
    if usr:
        prms["setts"] = loads(usr.settings)
    return render_template('book.html', **prms)


@app.route("/book/<book_name>/page/<page_num>", methods=["POST", "GET"])
def book_page_page(book_name, page_num):
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, page_num, usr = PageForm(), int(page_num), None
    book = db_sess.query(Book).filter(Book.name == book_name).first()
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            return redirect(url_for("main_page"))
    if not book or not (0 <= page_num < len(book.pages)):
        return redirect(url_for("main_page"))
    page = [pg for pg in book.pages if pg.number == page_num][0]
    if form.next.data:
        return redirect(url_for("book_page_page", book_name=book_name,
                                page_num=page_num + 1 if page_num + 1 < len(book.pages) else page_num))
    if form.prev.data:
        return redirect(url_for("book_page_page", book_name=book_name,
                                page_num=page_num - 1 if page_num - 1 >= 0 else 0))
    if form.comm_sub.data:
        comm = Comment(text=form.comm_field.data, author_id=usr_data[0], page_id=page.id, number=len(page.comments))
        db_sess.add(comm)
        db_sess.commit()
    prms = {
        "title": f'Книга {book_name}',
        "book": book,
        "page": page,
        "form": form,
        "usr": usr,
    }
    if usr:
        prms["setts"] = loads(usr.settings)
    return render_template('page.html', **prms)


@app.route("/settings", methods=["POST", "GET"])
def settings_page():
    global db_sess
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    form, usr = SettingsForm(), None
    if all(usr_data):
        usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                         User.name == usr_data[2]).first()
        if not usr:
            session.pop("id")
            session.pop("email")
            session.pop("name")
            return redirect(url_for("main_page"))
    prms = {
        "title": f'Настройки',
        "form": form,
        "user_id": usr_data[0],
    }
    setts = loads(usr.settings)
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
        usr.last_books = "[]"
    usr.settings = dumps(setts)
    db_sess.commit()
    form.change_name.data = usr.name
    form.change_about.data = usr.about
    form.font_color.data = setts["font-color"]
    form.font_size.data = setts["font-size"]
    form.font.data = setts["font"]
    form.ignore.data = setts["ignore"]
    form.check_books.data = setts["len-last-seen"]
    prms["setts"] = setts
    return render_template('settings.html', **prms)


def main():
    global db_sess
    global_init("db/main.db")
    db_sess = create_session()
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
    app.run(debug=True)


if __name__ == '__main__':
    main()
