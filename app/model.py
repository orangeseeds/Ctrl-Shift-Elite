from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, Text
from app.db import Base


room_user_table = Table(
    "rooms_users_table",
    Base.metadata,
    Column("room_id", ForeignKey("rooms.id")),
    Column("user_id", ForeignKey("users.id")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True)
    email = Column(String(30), unique=True)
    password = Column(String(30))
    rooms = relationship("Room", secondary=room_user_table,
                         back_populates="clients")


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    min_clients = Column(Integer)
    rounds = Column(Integer)
    code = Column(Text)
    sample = Column(Text)
    port = Column(Integer)
    clients = relationship(
        "User", secondary=room_user_table, back_populates="rooms")
