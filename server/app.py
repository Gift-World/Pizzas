#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(only=('id', 'name', 'address')) for r in restaurants])

    
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404 
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
  
        return jsonify(restaurant.to_dict(rules=('restaurant_pizzas',)))  # Include all relationships or specify as needed
    else:
        return make_response(jsonify(error="Restaurant not found")), 404

    
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas])       

@app.route('/pizzas/<int:id>', methods=['GET'])
def get_pizza(id):
    pizza = db.session.get(Pizza, id)
    if pizza:
        return jsonify(pizza.to_dict(only=('id', 'name', 'ingredients')))
    else:
        return make_response(jsonify(error="Pizza not found")), 404


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json

    try:
        restaurant = db.session.get(Restaurant, data['restaurant_id'])
        pizza = db.session.get(Pizza, data['pizza_id'])
        if not restaurant or not pizza:
            return jsonify({"errors": ["Restaurant or Pizza not found"]}), 404
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict(rules=('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas'))), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400
    except KeyError as e:
        return jsonify({"errors": [f"Missing key: {str(e)}"]}), 400
    except Exception as e:
        return jsonify({"errors": ["An unexpected error occurred"]}), 200

if __name__ == "__main__":
    app.run(port=5555, debug=True)
   
