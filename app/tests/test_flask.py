import pytest
from flask.testing import FlaskClient
from flask_app.models import Client, ClientParking, Parking
from flask_sqlalchemy import SQLAlchemy


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_route_status(client: FlaskClient, route):
    response = client.get(route)
    assert response.status_code == 200


def test_create_client(client: FlaskClient):
    client_data = {"name": "TestName", "surname": "TestSurname"}
    response = client.post("/clients", json=client_data)
    assert response.json["name"] == client_data["name"]
    assert response.json["surname"] == client_data["surname"]
    assert response.json["car_number"] == "None"
    assert response.json["credit_card"] == "None"


def test_create_parking(client: FlaskClient):
    # address: Mapped[str]
    # opened: Mapped[bool]
    # count_places: Mapped[int]
    # count_available_places: Mapped[int]
    parking_data = {
        "address": "test address",
        "opened": True,
        "count_places": 5,
        "count_available_places": 5,
    }
    response = client.post("/parkings", json=parking_data)
    print(response.json)
    assert response.json["address"] == str(parking_data["address"])
    assert response.json["opened"] == str(parking_data["opened"])
    assert response.json["count_places"] == str(parking_data["count_places"])
    assert response.json["count_available_places"] == str(
        parking_data["count_available_places"]
    )


@pytest.mark.parking
def test_client_parking_in(client: FlaskClient, db: SQLAlchemy):
    get_client: Client = db.session.query(Client).one()
    get_parking: Parking = db.session.query(Parking).one()
    before_count_places = get_parking.count_available_places
    client_parking_data = {"client_id": get_client.id, "parking_id": get_parking.id}
    assert get_parking.opened is True
    response = client.post("/client-parkings", json=client_parking_data)
    assert response.status_code == 200
    get_client_parking = db.session.get(ClientParking, int(response.json["id"]))
    assert get_client_parking is not None
    if get_client_parking is not None:
        assert get_client_parking.client_id == get_client.id
        assert get_client_parking.parking_id == get_parking.id
        assert get_client_parking.time_in is not None
        assert get_client_parking.time_out is None
        assert get_parking.count_available_places == before_count_places - 1


@pytest.mark.parking
def test_client_parking_out(client: FlaskClient, db: SQLAlchemy):
    get_client: Client = db.session.query(Client).one()
    get_parking: Parking = db.session.query(Parking).one()
    client_parking_data = {"client_id": get_client.id, "parking_id": get_parking.id}
    response = client.post("/client-parkings", json=client_parking_data)
    before_count_places = get_parking.count_available_places
    get_client_parking = db.session.get(ClientParking, int(response.json["id"]))
    response = client.delete("/client-parkings", json=client_parking_data)
    assert get_client_parking is not None
    if get_client_parking is not None:
        assert get_client_parking.client_id == get_client.id
        assert get_client_parking.parking_id == get_parking.id
        assert get_client_parking.time_in is not None
        assert get_client_parking.time_out is not None
        assert get_parking.count_available_places == before_count_places + 1
        assert get_client_parking.time_in < get_client_parking.time_out
