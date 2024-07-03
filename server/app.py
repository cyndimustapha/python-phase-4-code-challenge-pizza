from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

    def post(self):
        data = request.get_json()
        restaurant = Restaurant(name=data['name'], address=data['address'])
        db.session.add(restaurant)
        db.session.commit()
        return jsonify(restaurant.to_dict()), 201

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        return jsonify(restaurant.to_dict(include_pizzas=True))

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

class RestaurantPizzaResource(Resource):
    def get(self):
        restaurant_pizzas = []
        for restaurant_pizza in RestaurantPizza.query.all():
            restaurant_pizza_dict = restaurant_pizza.to_dict()
            restaurant_pizzas.append(restaurant_pizza_dict)
        response = make_response(restaurant_pizzas, 200)
        return response

    def post(self):
        json_data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=json_data.get("price"),
                restaurant_id=json_data.get("restaurant_id"),
                pizza_id=json_data.get("pizza_id")
            )
        except ValueError as exc:
            response_body = {"errors": ["validation errors"]}
            status = 400
            return (response_body, status)

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        restaurant_pizza_dict = new_restaurant_pizza.to_dict()
        response = make_response(restaurant_pizza_dict, 201)
        return response

api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
