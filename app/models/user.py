from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from passlib.hash import bcrypt

Base = declarative_base()

def hash_password(password: str) -> str:
    import bcrypt
    # Gera um salt e faz o hash da senha
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

class UserCreate(BaseModel):
    name: str
    password: str

class UserInDB(BaseModel):
    id: int
    name: str
    password: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
