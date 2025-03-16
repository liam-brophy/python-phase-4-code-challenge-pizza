#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        try:
            restaurants = Restaurant.query.all()
            restaurants_data = [restaurant.to_dict(include_pizzas=False) for restaurant in restaurants]
            return make_response(restaurants_data, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

api.add_resource(Restaurants, "/restaurants")


class RestaurantById(Resource):
    def get(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                restaurant_data = restaurant.to_dict(include_pizzas=True)
                return make_response(restaurant_data, 200)
            else:
                return make_response({"error": "Restaurant not found"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    def delete(self, id):
        try:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                RestaurantPizza.query.filter_by(restaurant_id=id).delete()
                db.session.delete(restaurant)
                db.session.commit()
                return make_response("", 204)
            else:
                return make_response({"error": "Restaurant not found"}, 404)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

api.add_resource(RestaurantById, "/restaurants/<int:id>")


class Pizzas(Resource):
    def get(self):
        try:
            # Bonus/experimentation: Searching
            search_query = request.args.get('search', '') 

            # Filtering
            if search_query:
                pizzas = Pizza.query.filter(
                    Pizza.name.ilike(f'%{search_query}%') |
                    Pizza.ingredients.ilike(f'%{search_query}%')
                ).all()
            else:
                pizzas = Pizza.query.all()

            pizzas_data = [pizza.to_dict() for pizza in pizzas]
            return make_response(pizzas_data, 200)
        
        except Exception as e:
            return make_response({"error": str(e)}, 500)

api.add_resource(Pizzas, "/pizzas")


class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()

            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            # validate
            if not price or not pizza_id or not restaurant_id:
                return make_response({"errors": ["validation errors"]}, 400)
            if price < 1 or price > 30:
                return make_response({"errors": ["validation errors"]}, 400)

            # create
            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()

            response_data = restaurant_pizza.to_dict()
            return make_response(response_data, 201)
        except Exception as e:
            return make_response({"errors": ["validation errors"]}, 400)
        

#Bonus/Experiemntation: Updating
    def patch(self, id):
        try:
            data = request.get_json()

            restaurant_pizza = db.session.get(RestaurantPizza, id)
            if not restaurant_pizza:
                return make_response({"error": "RestaurantPizza not found"}, 404)

            if "price" in data:
                price = data["price"]
                if price < 1 or price > 30:
                    return make_response({"errors": ["Price must be between 1 and 30"]}, 400)
                restaurant_pizza.price = price

            if "pizza_id" in data:
                restaurant_pizza.pizza_id = data["pizza_id"]

            if "restaurant_id" in data:
                restaurant_pizza.restaurant_id = data["restaurant_id"]

            db.session.commit()

            response_data = restaurant_pizza.to_dict()
            return make_response(response_data, 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas", "/restaurant_pizzas/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
