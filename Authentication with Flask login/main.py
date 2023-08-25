from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(1000))

@app.route('/')
def home():
    # with get_session() as session:
    #     pass
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        with get_session() as session:
            if session.query(User).filter(User.email == request.form.get("email")).first():
                flash("You've already signed up with that email, log in instead!")
                return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            name=request.form.get("name"),
            email=request.form.get("email"),
            password=hash_and_salted_password
        )
        with get_session() as session:
            session.add(new_user)
            session.commit()

            login_user(new_user)
        return redirect(url_for('secrets'))

    return render_template("register.html")


@login_manager.user_loader
def load_user(user_id):
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        return user


@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        with get_session() as session:
            loaded_user = session.query(User).filter(User.email == email).first()
            if loaded_user:
                if check_password_hash(loaded_user.password, password):
                    login_user(loaded_user)
                    return redirect(url_for('secrets'))
                else:
                    flash('Password incorrect, please try again.')
            else:
                flash("That email does not exist, please try again.")

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory("static/files", "cheat_sheet.pdf")
    pass


def get_session() -> Session:
    con = db.get_engine()
    session = Session(con)
    return session


if __name__ == "__main__":
    app.run(debug=True)
