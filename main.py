from data.db_session import create_session, global_init
from data.users import User
import datetime
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.main_page import MainPageForm
from forms.profile import ProfileForm
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
    if form.profile.data:
        return redirect(url_for("profile_page"))
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


@app.route("/profile", methods=["POST", "GET"])
def profile_page():
    global db_sess
    form = ProfileForm()
    usr_data = [session.get("id", None), session.get("email", None), session.get("password", None)]
    if form.validate_on_submit() and all(usr_data):
        session.pop("id")
        session.pop("email")
        session.pop("password")
        return redirect(url_for("main_page"))
    elif not all(usr_data):
        return redirect(url_for("main_page"))
    usr_name = db_sess.query(User).filter(User.id == usr_data[0]).first().name
    return render_template('profile.html', title=f'Профиль {usr_name}', form=form, name=usr_name)


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


def main():
    global db_sess
    global_init("db/main.db")
    db_sess = create_session()
    app.run()


if __name__ == '__main__':
    main()
