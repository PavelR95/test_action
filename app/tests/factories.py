import random
from typing import Any

import factory
from faker import Faker
from flask_app.models import DATABASE, Client, Parking

faker = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = DATABASE.session

    name = faker.first_name()
    surname = faker.last_name()
    car_number = faker.text(max_nb_chars=10)
    credit_card = faker.credit_card_number()


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = DATABASE.session

    address: str = faker.address()
    opened: bool = faker.boolean()
    count_places: int = random.randint(5, 10)
    count_available_places: Any = factory.LazyAttribute(lambda x: random.randint(0, 5))
