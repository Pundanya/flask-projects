from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
import random

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

@app.route("/random", methods=["GET"])
def get_random_cafe():
    with get_session() as session:
        cafes = session.query(Cafe).all()
        random_cafe = random.choice(cafes)
        return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all():
    with get_session() as session:
        cafes = session.query(Cafe).all()
        all_json = {
            "cafes": [cafe.to_dict() for cafe in cafes]
        }
        return jsonify(all_json)


@app.route("/search", methods=["GET"])
def search():
    location = request.args["loc"]
    with get_session() as session:
        searched_cafes = session.query(Cafe).filter(Cafe.location == location).all()
        if searched_cafes:
            all_json = {
                "cafes": [cafe.to_dict() for cafe in searched_cafes]
            }
            return jsonify(all_json)
        else:
            return jsonify(
                {
                    "error": {
                        "Not Found": "Sorry, we don't have a cafe at that location."
                    }
                }
            )


@app.route("/add", methods=["POST"])
def post_new_cafe():
    with get_session() as session:
        new_cafe = Cafe(
            name=request.args.get("name"),
            map_url=request.args.get("map_url"),
            img_url=request.args.get("img_url"),
            location=request.args.get("loc"),
            has_sockets=bool(request.args.get("sockets")),
            has_toilet=bool(request.args.get("toilet")),
            has_wifi=bool(request.args.get("wifi")),
            can_take_calls=bool(request.args.get("calls")),
            seats=request.args.get("seats"),
            coffee_price=request.args.get("coffee_price"),
        )
        session.add(new_cafe)
        print(new_cafe.to_dict())
        session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<string:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args["new_price"]
    with get_session() as session:
        cafe = session.query(Cafe).filter(Cafe.id == cafe_id).first()
        if cafe:
            cafe.coffee_price = new_price
            session.commit()
            return jsonify(response={"success": "Successfully updated the price."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report-closed/<string:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args["api_key"]
    if api_key == "TopSecretAPIKey":
        with get_session() as session:
            cafe_to_delete = session.query(Cafe).filter(Cafe.id == cafe_id).first()
            if cafe_to_delete:
                session.delete(cafe_to_delete)
                session.commit()
                return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
            else:
                return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


def get_session() -> Session:
    connection = db.get_engine()
    session = Session(connection)
    return session


if __name__ == '__main__':
    app.run(debug=True)
