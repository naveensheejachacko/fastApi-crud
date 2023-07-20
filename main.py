from fastapi import FastAPI,Depends,HTTPException,Request,Response
from sqlalchemy.orm import Session

from . import crud,models,schemas
from .database import SessionLocal,engine

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

"""Dependency
 independent database session/connection (SessionLocal)
 per request, use the same session through 
 all the request and then close it after
 the request is finished.
 For that, we will create a new dependency with yield """

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# create middleware

@app.middleware("http")
async def db_session_middleware(request: Request,call_next):
    response = Response("internal sever down",status_code=500)
    try:
        request.state.db = SessionLocal()
        response =  await call_next(request)
    finally:
        request.state.db.close()
    return response

#Dependency
def get_db(request: Request):
    return request.state.db


@app.post("/users/",response_model = schemas.User)
def create_user(user: schemas.UserCreate, db: Session =  Depends(get_db)):
    db_user = crud.get_user_by_email(db,email=user.email)
    if db_user:
        raise HTTPException(status_code= 400, detail="email already exist")
    return crud.create_user(db=db, user=user)

@app.get("/users/",response_model =  list[schemas.User])
def read_users(skip: int=0 , limit: int = 100, db:Session = Depends(get_db)):
    users = crud.get_users(db, skip= skip, limit = limit)
    return users

@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db = db, item = item, user_id = user_id)

@app.get("/items", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip = skip, limit = limit)
    return items