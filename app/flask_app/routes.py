import logging
from datetime import datetime
from typing import Any, List

from flask import Blueprint, request
from flask_app.models import DATABASE, Client, ClientParking, Parking
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

app_routes = Blueprint("route", __name__)
db = DATABASE

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(name="Flask_APP")


@app_routes.route("/clients", methods=["GET"])
def get_clients() -> Any:
    session: Session = db.session
    client_list: List[Client] = session.query(Client).all()
    log.debug("GET ALL CLIENT: %s", client_list)
    return [client.to_json() for client in client_list]


@app_routes.route("/clients/<int:client_id>", methods=["GET"])
def get_client_by_id(client_id: int) -> Any:
    session: Session = db.session
    client: Client | None = session.get(Client, client_id)
    if client is None:
        return {"NotFound"}, 404
    log.debug("GET CLIENT %s", client)
    return client.to_json(), 200


@app_routes.route("/clients", methods=["POST"])
def create_client() -> tuple[dict[str, str], int]:
    session: Session = db.session
    client_json: dict = request.json
    new_client = Client()
    new_client.set_attributes(client_json)
    try:
        session.add(new_client)
        session.commit()
    except IntegrityError as err:
        return {"error": str(err)}, 400
    log.debug("CREATE CLIENT: %s", new_client)
    return new_client.to_json(), 200


@app_routes.route("/parkings", methods=["POST"])
def create_parking() -> tuple[dict[str, str], int]:
    session: Session = db.session
    parking_json: dict = request.json
    new_parking = Parking()
    new_parking.set_attributes(parking_json)
    try:
        session.add(new_parking)
        session.commit()
    except IntegrityError as err:
        return {"error": str(err)}, 400
    log.debug("CREATE PARKING: %s", new_parking)
    return new_parking.to_json(), 200


@app_routes.route("/client-parkings", methods=["POST"])
def create_client_parkings():
    session: Session = db.session
    data = request.json
    try:
        client_id = data["client_id"]
        parking_id = data["parking_id"]
    except KeyError as err:
        return {"error": "Not value <{}>".format(str(err))}, 400
    get_client = session.get(Client, client_id)
    log.debug("GET %s", get_client)
    if get_client is None:
        return {"error": "Not found client by id={}".format(client_id)}, 400
    get_parking = session.get(Parking, parking_id)
    log.debug("GET %s", get_parking)
    if get_parking is None:
        return {"error": "Not found parking by id={}".format(parking_id)}, 400
    if not get_parking.opened:
        return {"error": "Parking id={} is closed".format(parking_id)}, 400
    if get_parking.count_available_places == 0:
        return {
            "error": "Parking id={} is not available places".format(parking_id)
        }, 400
    # GET ClientParking
    try:
        client_parking = (
            session.query(ClientParking)
            .filter(
                ClientParking.client_id == client_id,
                ClientParking.parking_id == parking_id,
            )
            .one()
        )
        log.debug("GET %s", client_parking)
        if client_parking.time_in is not None:
            return {"error": "Client is already in the parking"}
    except NoResultFound:
        client_parking = ClientParking()
        client_parking.client = get_client
        client_parking.parking = get_parking
        log.debug("CREATE %s", client_parking)
    # SET Time in and SAVE
    try:
        client_parking.time_in = datetime.now()
        session.add(client_parking)
        session.commit()
    except IntegrityError as err:
        return {"error": str(err)}, 400
    try:
        get_parking.reduce_count_available_places()
    except ValueError as err:
        return {"error server": str(err)}, 500

    return client_parking.to_json()


@app_routes.route("/client-parkings", methods=["DELETE"])
def delete_client_parkings():
    session: Session = db.session
    data = request.json
    try:
        client_id = data["client_id"]
        parking_id = data["parking_id"]
    except KeyError as err:
        return {"error": "Not value <{}>".format(str(err))}, 400
    get_client = session.get(Client, client_id)
    log.debug("GET %s", get_client)
    if get_client is None:
        return {"error": "Not found client by id={}".format(client_id)}, 400
    get_parking = session.get(Parking, parking_id)
    log.debug("GET %s", get_parking)
    if get_parking is None:
        return {"error": "Not found parking by id={}".format(parking_id)}, 400
    try:
        get_client_parking = (
            session.query(ClientParking)
            .filter(
                ClientParking.client_id == client_id,
                ClientParking.parking_id == parking_id,
            )
            .one()
        )
        log.debug("GET %s", get_client_parking)
    except NoResultFound:
        return {
            "error": f"Not found client parking by "
            f"client_id={client_id} parking_id={parking_id}"
        }, 400
    if get_client_parking.time_out is not None:
        return {"error": "Client parking already deleted"}
    if get_client.credit_card is None:
        return {"error": "Client card not linked"}
    get_client_parking.time_out = datetime.now()
    get_parking.increase_count_available_places()
    db.session.commit()
    return get_client_parking.to_json()
