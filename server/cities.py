import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from flask import Blueprint, jsonify, request, abort

cities_bp = Blueprint("cities", __name__)

DATA_PATH = Path(
    os.environ.get("CITY_DATA_PATH", Path(__file__).resolve().parents[1] / "data" / "cities.json")
)

@dataclass
class City:
    id: int
    name: str
    state: Optional[str] = None
    country_code: Optional[str] = None
    population: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

def _load() -> List[City]:
    if not DATA_PATH.exists():
        return []
    raw = json.loads(DATA_PATH.read_text() or "[]")
    return [City(**item) for item in raw]

def _save(items: List[City]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps([asdict(c) for c in items], indent=2))

def _next_id(items: List[City]) -> int:
    return (max([c.id for c in items]) + 1) if items else 1

@cities_bp.get("/cities")
def list_cities():
    """
    List cities
    ---
    tags:
      - cities
    responses:
      200:
        description: List of cities
        schema:
          type: array
          items:
            $ref: '#/definitions/City'
    definitions:
      City:
        type: object
        properties:
          id: {type: integer}
          name: {type: string}
          state: {type: string}
          country_code: {type: string}
          population: {type: integer}
          lat: {type: number}
          lon: {type: number}
    """
    return jsonify([asdict(c) for c in _load()])

@cities_bp.get("/cities/<int:city_id>")
def get_city(city_id: int):
    """
    Get city by id
    ---
    tags: [cities]
    parameters:
      - in: path
        name: city_id
        required: true
        type: integer
    responses:
      200: {description: City found, schema: {$ref: '#/definitions/City'}}
      404: {description: Not found}
    """
    for c in _load():
        if c.id == city_id:
            return jsonify(asdict(c))
    abort(404, description="City not found")

@cities_bp.post("/cities")
def create_city():
    """
    Create a city
    ---
    tags: [cities]
    parameters:
      - in: body
        name: city
        required: true
        schema:
          $ref: '#/definitions/City'
    responses:
      201: {description: Created, schema: {$ref: '#/definitions/City'}}
      400: {description: Bad request}
    """
    payload = request.get_json(silent=True) or {}
    if "name" not in payload:
        abort(400, description="'name' is required")
    items = _load()
    city = City(
        id=_next_id(items),
        name=payload["name"],
        state=payload.get("state"),
        country_code=payload.get("country_code"),
        population=payload.get("population"),
        lat=payload.get("lat"),
        lon=payload.get("lon"),
    )
    items.append(city)
    _save(items)
    return jsonify(asdict(city)), 201

@cities_bp.put("/cities/<int:city_id>")
def update_city(city_id: int):
    """
    Update a city
    ---
    tags: [cities]
    parameters:
      - in: path
        name: city_id
        required: true
        type: integer
      - in: body
        name: city
        required: true
        schema:
          $ref: '#/definitions/City'
    responses:
      200: {description: Updated, schema: {$ref: '#/definitions/City'}}
      404: {description: Not found}
    """
    payload = request.get_json(silent=True) or {}
    items = _load()
    for i, c in enumerate(items):
        if c.id == city_id:
            updated = City(
                id=c.id,
                name=payload.get("name", c.name),
                state=payload.get("state", c.state),
                country_code=payload.get("country_code", c.country_code),
                population=payload.get("population", c.population),
                lat=payload.get("lat", c.lat),
                lon=payload.get("lon", c.lon),
            )
            items[i] = updated
            _save(items)
            return jsonify(asdict(updated))
    abort(404, description="City not found")

@cities_bp.delete("/cities/<int:city_id>")
def delete_city(city_id: int):
    """
    Delete a city
    ---
    tags: [cities]
    parameters:
      - in: path
        name: city_id
        required: true
        type: integer
    responses:
      204: {description: Deleted}
      404: {description: Not found}
    """
    items = _load()
    keep = [c for c in items if c.id != city_id]
    if len(keep) == len(items):
        abort(404, description="City not found")
    _save(keep)
    return ("", 204)
