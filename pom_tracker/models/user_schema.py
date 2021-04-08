from pydantic import BaseModel
from fastapi import Form


class User(BaseModel):
    email: str = Form(...)


class UserLogin(User):
    password: str = Form(...)


class UserCreate(User):
    first_name: str = Form(...)
    middle_name: str = Form(...)
    last_name: str = Form(...)
    display_name: str = Form(...)
    password: str = Form(...)
