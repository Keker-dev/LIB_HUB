from flask import Flask
from flask import url_for, request, render_template, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'libhub_secret_key'


@app.route("/")
def main_page():
    return render_template("base.html")


def main():
    app.run()


if __name__ == '__main__':
    main()
