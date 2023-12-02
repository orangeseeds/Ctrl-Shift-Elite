from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class Room(BaseModel):
    id: int
    min_clients: int
    rounds: int
    code: str
    sample: str
    # clients: []User

    class Config:
        orm_mode = True
