from flask import Blueprint, jsonify, request
from server.database import db
from server.models.city_model import City

city_bp = Blueprint("city_bp", __name__, url_prefix="/city")


@city_bp.get("/")
def get_all_cities():
    cities = City.query.all()
    return jsonify([c.to_dict() for c in cities]), 200


@city_bp.get("/<int:city_id>")
def get_city(city_id):
    city = City.query.get(city_id)
    if not city:
        return jsonify({"error": "City not found"}), 404
    return jsonify(city.to_dict()), 200


@city_bp.post("/")
def create_city():
    data = request.get_json() or {}
    name = data.get("name")
    state_id = data.get("state_id")

    if not name or not state_id:
        return jsonify({"error": "name and state_id are required"}), 400

    city = City(name=name, state_id=state_id)
    db.session.add(city)
    db.session.commit()

    return jsonify(city.to_dict()), 201


@city_bp.put("/<int:city_id>")
def update_city(city_id):
    city = City.query.get(city_id)
    if not city:
        return jsonify({"error": "City not found"}), 404

    data = request.get_json() or {}

    city.name = data.get("name", city.name)
    city.state_id = data.get("state_id", city.state_id)

    db.session.commit()
    return jsonify(city.to_dict()), 200


@city_bp.delete("/<int:city_id>")
def delete_city(city_id):
    city = City.query.get(city_id)
    if not city:
        return jsonify({"error": "City not found"}), 404

    db.session.delete(city)
    db.session.commit()
    return jsonify({"message": "City deleted"}), 200
