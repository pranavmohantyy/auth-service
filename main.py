from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
from passlib.context import CryptContext
import re
import jwt

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

class Token:
    access_token: str
    token_type: str

class TokenData:
    email: str | None = None

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, "secret", algorithm="HS256")
    return token

@app.post("/register/")
async def register(email: str, password: str):
    db: Session = SessionLocal()
    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/")
async def login(email: str, password: str):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/verify-email/")
async def verify_email(email: str, background_tasks: BackgroundTasks):
    token = create_access_token(data={"sub": email}, expires_delta=datetime.timedelta(minutes=10))
    background_tasks.add_task(fake_send_email, email, token)
    return {"msg": "Verification email sent"}

def fake_send_email(email: str, token: str):
    print(f"Sending verification email to {email} with token {token}")