from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}

@app.get("/add")
def add(a: int, b: int):
    return {"result":a + b}

@app.get("/minus")
def add(a: int, b:int):
    return {"result": a - b}

from pydantic import BaseModel

class Item(BaseModel):
    name : str
    price : int

@app.post("/item")
def create_item(item: Item):
    return {
        "name": item.name,
        "price": item.price
    }

class User(BaseModel):
    name : str
    age : int

@app.post("/user")
def create_user(user: User):
    return {
        "message": f"{user.name} 등록 완료",
        "age": user.age
    }

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

from sqlalchemy import Column, Integer, String

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user: User, db: Session = Depends(get_db)):

    new_user = UserDB(
        username=user.name,
        password="1234",
    )

    db.add(new_user)
    db.commit()

    return {"message": "회원가입 완료"}

@app.get("/login")
def login(name : str, password : str, db : Session = Depends(get_db)):

    db_user = db.query(UserDB).filter((UserDB.username == name) & (UserDB.password == password)).first()

    if not db_user:
        return {"message" : "사용자 정보가 올바르지 않음"}
    
    return {"message" : "로그인 성공"}

@app.get("/modify")
def login(name : str, newpassword : str, db : Session = Depends(get_db)):

    db_user = db.query(UserDB).filter(UserDB.username == name).first()

    if not db_user:
        return {"message" : "사용자 정보가 올바르지 않음"}
    
    db.password = newpassword
    db.commit()
    return {"message" : f"{newpassword}로 비밀번호 수정 완료"}