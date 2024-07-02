#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
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
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        return jsonify(restaurant.to_dict())

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

class RestaurantPizzaResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('price', type=int, required=True, help='Price is required')
        parser.add_argument('pizza_id', type=int, required=True, help='Pizza ID is required')
        parser.add_argument('restaurant_id', type=int, required=True, help='Restaurant ID is required')
        args = parser.parse_args()

        if args['price'] < 1 or args['price'] > 30:
            return {"errors": ["Price must be between 1 and 30"]}, 400

        pizza = Pizza.query.get(args['pizza_id'])
        restaurant = Restaurant.query.get(args['restaurant_id'])

        if pizza is None or restaurant is None:
            return {"errors": ["Pizza or Restaurant not found"]}, 404

        restaurant_pizza = RestaurantPizza(price=args['price'], pizza=pizza, restaurant=restaurant)
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(restaurant_pizza.to_dict()), 201

api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)
