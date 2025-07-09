from fastapi import APIRouter, Body
from passlib.context import CryptContext

from src.schemas.users import UserRequestAdd, UserAdd
from src.repositories.users import UserRepository
from src.database import async_session_maker

router = APIRouter(prefix="/auth", tags=['Авторизация и аутентификация'])

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')


@router.post('/register', summary='Регистрация пользователя')
async def user_registet(data: UserRequestAdd = Body(openapi_examples={
    "1": {"summary": "Потап", "value": {
        "first_name": "Потапчик",
        "last_name": "Владонов",
        "nikname": "AlonMneVlom",
        "phone": "8800553535",
        "email": "potapvlad@gmail.com",
        "password": "трынь бам"
    }}
})):
    hashed_password = pwd_context.hash(data.password)
    new_user_data = UserAdd(first_name=data.first_name, last_name=data.last_name, nikname=data.nikname, phone=data.phone, email=data.email, hashed_password=hashed_password)
    async with async_session_maker() as session:
        await UserRepository(session).add(new_user_data)
        await session.commit()
    
    return {'status': 'ok'}