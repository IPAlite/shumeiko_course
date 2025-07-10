from pydantic import BaseModel, ConfigDict, EmailStr


class UserRequestAdd(BaseModel):
    first_name: str
    last_name: str
    nikname: str
    phone: str
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    first_name: str
    last_name: str
    nikname: str
    phone: str
    email: EmailStr
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    nikname: str
    phone: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
