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
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/request-reset/")
async def request_reset(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        token = jwt.encode({"sub": user.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, "secret")
        user.reset_token = token
        db.commit()
        # send email with token (placeholder)
        print(f"Send email to {email} with token {token}")
    return {"msg": "If an account with that email exists, a reset link has been sent."}

@app.post("/reset-password/")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if user and user.reset_token == token:
            user.hashed_password = pwd_context.hash(new_password)
            user.reset_token = None
            db.commit()
            return {"msg": "Password has been reset."}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")