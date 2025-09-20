from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext
import jwt

from fastapi import HTTPException, Response

from src.exceptions import ObjectAlredyExistsException, ObjectNotFoundException
from src.schemas.users import UserAdd, UserLogin, UserRequestAdd
from src.services.base import BaseService
from src.config import settings


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hashed_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Срок действия токена истек")

    async def get_me(self, user_id):
        return await self.db.users.get_one_or_none(id=user_id)

    async def user_register(self, data: UserRequestAdd):
        hashed_password = AuthService().hashed_password(password=data.password)
        new_user_data = UserAdd(
            first_name=data.first_name,
            last_name=data.last_name,
            nikname=data.nikname,
            phone=data.phone,
            email=data.email,
            hashed_password=hashed_password,
        )
        try:
            await self.db.users.add(new_user_data)
            await self.db.commit()

        except ObjectAlredyExistsException:
            raise HTTPException(
                status_code=409, detail="Пользователь с такой почтой уже существует"
            )

    async def user_login(self, data: UserLogin, response: Response):
        user = await self.db.users.get_one_or_none(email=data.email)
        if not user:
            raise HTTPException(
                status_code=401, detail="Пользователь с таким email не зарегистрирован"
            )
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Вы ввели неверный пароль")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return access_token

    async def user_delete(self, user_mail):
        try:
            await self.db.users.delete(email=user_mail)
        except ObjectNotFoundException:
            raise HTTPException(status_code=404, detail="Такого пользователя не существует")
        await self.db.commit()
