from pydantic import BaseModel
from fastapi import Form


class User(BaseModel):
    email: str


class UserLogin(User):
    password: str


class UserCreate(User):
    first_name: str
    middle_name: str
    last_name: str
    display_name: str
    password: str
