from flask.testing import FlaskClient
from flask_app.models import Client, Parking
from flask_sqlalchemy import SQLAlchemy

from .factories import ClientFactory, ParkingFactory


def test_create_client(client: FlaskClient, db: SQLAlchemy):
    new_client = ClientFactory()
    client_json = {
        "name": new_client.name,
        "surname": new_client.surname,
        "car_number": new_client.car_number,
        "credit_card": new_client.credit_card,
    }
    before_count_lines_db = db.session.query(Client).count()
    response = client.post("/clients", json=client_json)
    after_count_lines_db = db.session.query(Client).count()
    assert after_count_lines_db == before_count_lines_db + 1
    assert response.json["id"] != "None"
    assert response.json["name"] == client_json["name"]
    assert response.json["surname"] == client_json["surname"]
    assert response.json["car_number"] == str(client_json["car_number"])
    assert response.json["credit_card"] == str(client_json["credit_card"])


def test_create_parking(client: FlaskClient, db: SQLAlchemy):
    new_parking = ParkingFactory()
    parking_json = {
        "address": new_parking.address,
        "opened": new_parking.opened,
        "count_places": new_parking.count_places,
        "count_available_places": new_parking.count_available_places,
    }
    before_count_lines_db = db.session.query(Parking).count()
    response = client.post("/parkings", json=parking_json)
    after_count_lines_db = db.session.query(Parking).count()
    assert after_count_lines_db == before_count_lines_db + 1
    assert response.json["id"] != "None"
    assert response.json["address"] == str(parking_json["address"])
    assert response.json["opened"] == str(parking_json["opened"])
    assert response.json["count_places"] == str(parking_json["count_places"])
    assert response.json["count_available_places"] == str(
        parking_json["count_available_places"]
    )
