import flask_app
import pytest
from flask import Flask
from flask_app.models import Client, ClientParking, Parking

_db = flask_app.DATABASE


@pytest.fixture
def app():
    flask_app.SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    flask_app.TESTING = True
    _app = flask_app.initial_app()

    with _app.app_context():
        _db.create_all()
        # Create Client
        client = Client(
            name="test",
            surname="test",
            credit_card="2543254325432543",
            car_number="1234567890",
        )
        _db.session.add(client)
        # Create Parking
        parking = Parking(
            address="test_address",
            opened=True,
            count_places=5,
            count_available_places=5,
        )
        _db.session.add(parking)
        _db.session.commit()
        # Create ClientParking
        client_parking = ClientParking()
        client_parking.client = client
        client_parking.parking = parking
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app: Flask):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app: Flask):
    with app.app_context():
        yield _db
