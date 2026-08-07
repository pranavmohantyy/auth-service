from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
from passlib.context import CryptContext
import re
import jwt
import smtplib

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_locked = Column(Boolean, default=False)
    failed_attempts = Column(Integer, default=0)
    lock_until = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login/")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        if user.is_locked:
            if user.lock_until and user.lock_until > datetime.datetime.now():
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is locked. Try again later.")
            user.is_locked = False
            user.failed_attempts = 0
        if not verify_password(password, user.password):
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.is_locked = True
                user.lock_until = datetime.datetime.now() + datetime.timedelta(minutes=15)
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user.failed_attempts = 0
        db.commit()
        return {"access_token": "some_token", "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

def verify_password(plain_password, hashed_password):
    return CryptContext(schemes=["bcrypt"]).verify(plain_password, hashed_password)
