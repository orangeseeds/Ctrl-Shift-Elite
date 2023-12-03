from datetime import timedelta
from fastapi import Depends, FastAPI, Request, Form, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from app.db import SessionLocal, engine
import app.jwt as jwt
import app.model as model
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import server
from threading import Thread

HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", 8000)

'''
Routes:
    GET / -> landing.
    GET /rooms ->  gets all rooms.
    POST /rooms -> create new room.
    DELETE /rooms/:id -> delete a room
    GET /rooms/:id -> get specific room
    GET /dashboard -> get my dashboard
'''

app = FastAPI()
model.Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("signup_form.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
def signup(request: Request,
           name: Annotated[str, Form()],
           email: Annotated[str, Form()],
           password: Annotated[str, Form()],
           confirm_password: Annotated[str, Form()],
           db: Session = Depends(get_database_session),
           ):
    jwt.create_user(db, name, email, password)
    response = RedirectResponse('/rooms', status_code=303)
    return response


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("login_form.html", {"request": request})


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_database_session)):
    user = jwt.authenticate_user(db,
                                 form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/rooms", response_class=HTMLResponse)
def get_rooms(request: Request, db: Session = Depends(get_database_session)):

    rooms = db.query(model.Room).all()
    return templates.TemplateResponse("rooms.html", {
        "request": request,
        "rooms": rooms
    })


@app.get("/rooms/create", response_class=HTMLResponse)
def room_form(request: Request, db: Session = Depends(get_database_session)):
    return templates.TemplateResponse("room_form.html", {
        "request": request
    })


@app.post("/rooms/store")
async def room_store(
    min_clients: Annotated[int, Form()],
    iterations: Annotated[int, Form()],
    modelCode: Annotated[str, Form()],
    modelData: Annotated[str, Form()],
    port: Annotated[str, Form()],
    current_user: Annotated[model.User, Depends(jwt.get_current_active_user)],
    db: Session = Depends(get_database_session),
):
    room = model.Room(
        min_clients=min_clients,
        rounds=iterations,
        code=modelCode,
        sample=modelData,
        port = port,
    )

    usr = jwt.get_user(db, current_user.email)
    room.clients.append(usr)

    db.add(room)
    db.commit()
    db.refresh(room)
    response = RedirectResponse('/rooms/create', status_code=303)
    return response


CURR_PORT = 8001

def worker(room, port):
    server.server.start_server(
    server_address=f"localhost:{port}",
    config=server.server.ServerConfig(num_rounds=room.rounds),
    grpc_max_message_length=1024*1024*1024,
    strategy=server.strategy
    )

@app.post("/room/{room_id}/start")
def start_room_model(
    room_id:int,
    current_user: Annotated[model.User, Depends(jwt.get_current_active_user)],
    db: Session = Depends(get_database_session),
):
    room = db.query(model.Room).filter(model.Room.id == room_id).first()
    p = CURR_PORT
    print(room.port)
    if(room):
        t = Thread(target=worker, args=(room,room.port))
        t.start()
    # worker(room, 8002)
    return {"started":room}

