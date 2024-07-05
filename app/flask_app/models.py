from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DATETIME, Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseModel(DeclarativeBase):
    pass


DATABASE = SQLAlchemy(model_class=BaseModel)


class Client(BaseModel):

    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    credit_card: Mapped[str] = mapped_column(String(50), nullable=True)
    car_number: Mapped[str] = mapped_column(String(10), nullable=True)

    parking: Mapped[List["ClientParking"]] = relationship(back_populates="client")

    def set_attributes(self, attrs_dict: dict) -> None:
        for atr_name in self.__annotations__.keys():
            atr = self.__getattribute__(atr_name)
            if not isinstance(atr, list):
                self.__setattr__(atr_name, attrs_dict.get(atr_name))

    def __repr__(self) -> str:
        atr_value_list = [
            "{}:{}".format(atr_name, str(self.__getattribute__(atr_name)))
            for atr_name in self.__annotations__.keys()
            if not isinstance(self.__getattribute__(atr_name), list)
            and not isinstance(
                self.__getattribute__(atr_name), tuple(DATABASE.Model.__subclasses__())
            )
        ]
        cls_name = self.__class__.__name__
        answer = "; ".join(atr_value_list)
        return f"{cls_name} {answer}"

    def to_json(self) -> dict:
        answer = {}
        for key_atr in self.__annotations__.keys():
            atr = self.__getattribute__(key_atr)
            if not isinstance(atr, list) and not isinstance(
                atr, tuple(DATABASE.Model.__subclasses__())
            ):
                answer[key_atr] = str(self.__getattribute__(key_atr))
        return answer


class Parking(BaseModel):

    __tablename__ = "parking"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    opened: Mapped[bool] = mapped_column(Boolean, nullable=True)
    count_places: Mapped[int] = mapped_column(Integer, nullable=False)
    count_available_places: Mapped[int] = mapped_column(Integer, nullable=False)

    client: Mapped[List["ClientParking"]] = relationship(back_populates="parking")

    def set_attributes(self, attrs_dict: dict) -> None:
        for atr_name in self.__annotations__.keys():
            atr = self.__getattribute__(atr_name)
            if not isinstance(atr, list):
                self.__setattr__(atr_name, attrs_dict.get(atr_name))

    def __repr__(self) -> str:
        atr_value_list = [
            "{}:{}".format(atr_name, str(self.__getattribute__(atr_name)))
            for atr_name in self.__annotations__.keys()
            if not isinstance(self.__getattribute__(atr_name), list)
            and not isinstance(
                self.__getattribute__(atr_name), tuple(DATABASE.Model.__subclasses__())
            )
        ]
        cls_name = self.__class__.__name__
        answer = "; ".join(atr_value_list)
        return f"{cls_name} {answer}"

    def to_json(self) -> dict:
        answer = {}
        for key_atr in self.__annotations__.keys():
            atr = self.__getattribute__(key_atr)
            if not isinstance(atr, list) and not isinstance(
                atr, tuple(DATABASE.Model.__subclasses__())
            ):
                answer[key_atr] = str(self.__getattribute__(key_atr))
        return answer

    def reduce_count_available_places(self):
        if self.count_available_places == 0:
            raise ValueError("The count available places cannot be less than 0")
        self.count_available_places -= 1

    def increase_count_available_places(self):
        if self.count_available_places == self.count_places:
            raise ValueError(
                "The count available places cannot be more than total places"
            )
        self.count_available_places += 1


class ClientParking(BaseModel):

    __tablename__ = "client_parking"
    __table_args__ = (
        UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    parking_id: Mapped[int] = mapped_column(ForeignKey("parking.id"), nullable=False)
    time_in: Mapped[DATETIME] = mapped_column(DATETIME, nullable=True)
    time_out: Mapped[DATETIME] = mapped_column(DATETIME, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="parking")
    parking: Mapped["Parking"] = relationship(back_populates="client")

    def __repr__(self) -> str:
        atr_value_list = [
            "{}:{}".format(atr_name, str(self.__getattribute__(atr_name)))
            for atr_name in self.__annotations__.keys()
            if not isinstance(self.__getattribute__(atr_name), list)
            and not isinstance(
                self.__getattribute__(atr_name), tuple(DATABASE.Model.__subclasses__())
            )
        ]
        cls_name = self.__class__.__name__
        answer = "; ".join(atr_value_list)
        return f"{cls_name} {answer}"

    def to_json(self) -> dict:
        answer = {}
        for key_atr in self.__annotations__.keys():
            atr = self.__getattribute__(key_atr)
            if not isinstance(atr, list) and not isinstance(
                atr, tuple(DATABASE.Model.__subclasses__())
            ):
                answer[key_atr] = str(self.__getattribute__(key_atr))
        return answer
