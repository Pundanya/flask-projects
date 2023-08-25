import copy

from flask_bootstrap import Bootstrap
from sqlalchemy import desc
from wtforms import Form, StringField, validators, FloatField
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
import movieapi

API_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-sqlalchemy.db"
db.init_app(app)

Bootstrap(app)


class Movie(db.Model):
    __tablename__ = "Movies"
    __table_args__ = {"comment": "Table of top 10 movies"}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    year = db.Column(db.Integer)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))


class EditForm(Form):
    rating = FloatField('Rating', [validators.InputRequired(), validators.DataRequired()])
    review = StringField('Review', [validators.InputRequired()])


class AddForm(Form):
    title = StringField("Title", [validators.InputRequired()])


@app.route("/")
def home():
    with get_session() as session:
        all_movies = session.query(Movie).order_by(desc(Movie.rating)).all()[::-1]
        for i in range(len(all_movies)):
            all_movies[i].ranking = len(all_movies) - i
            session.merge(all_movies[i])
        session.flush()
        all_m_copy = copy.deepcopy(all_movies)
        session.commit()
    return render_template("index.html", all_movies=all_m_copy)


@app.route('/edit', methods=["GET", "POST"])
def edit():
    requested_id = request.args["id"]
    form = EditForm(request.form)
    if request.method == 'POST':
        new_rating = float(form.rating.data)
        new_review = form.review.data
        with get_session() as session:
            edited_movie = session.query(Movie).filter(Movie.id == requested_id).first()
            edited_movie.rating = new_rating
            edited_movie.review = new_review
            session.merge(edited_movie)
            session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", form=form, id=requested_id)


@app.route("/select/<movie_to_search>")
def select_movie(movie_to_search):
    movie_list = movieapi.get_movies(movie_to_search)
    return render_template("select.html", movie_list=movie_list)


@app.route("/find")
def get_movie_data():
    movie_api_id = request.args.get("movie_id")
    if movie_api_id:
        movie_data = movieapi.find_movie(movie_api_id)
        new_movie = Movie(
            title=movie_data["title"],
            year=movie_data["release_date"].split("-")[0],
            img_url=API_IMAGE_URL + movie_data["poster_path"],
            description=movie_data["overview"],
            ranking=int(movie_data["vote_average"])
        )
        with get_session() as session:
            session.add(new_movie)
            session.flush()
            movie_id = new_movie.id
            session.commit()
        return redirect(url_for("edit", id=movie_id))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_form = AddForm(request.form)
    if request.method == "POST":
        movie_to_search = add_form.title.data
        return redirect(url_for("select_movie", movie_to_search=movie_to_search))

    return render_template("add.html", add_form=add_form)


@app.route("/delete", methods=["GET"])
def delete_movie():
    requested_id = request.args["id"]
    with get_session() as session:
        movie_to_delete = session.query(Movie).filter(Movie.id == requested_id).first()
        session.delete(movie_to_delete)
        session.commit()
    return redirect(url_for("home"))


def get_session() -> Session:
    con = db.get_engine()
    session = Session(con)
    return session


if __name__ == '__main__':
    app.run(debug=True)
