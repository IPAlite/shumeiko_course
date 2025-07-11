from fastapi import APIRouter, HTTPException, Response, Request, Body

from src.config import settings
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.repositories.users import UserRepository
from src.database import async_session_maker
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=['Авторизация и аутентификация'])


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
    hashed_password = AuthService().hashed_password(password=data.password)
    new_user_data = UserAdd(first_name=data.first_name, last_name=data.last_name, nikname=data.nikname, phone=data.phone, email=data.email, hashed_password=hashed_password)
    async with async_session_maker() as session:
        await UserRepository(session).add(new_user_data)
        await session.commit()
    
    return {'status': 'ok'}


@router.post('/login', summary='Аутентификация пользователя')
async def user_login(data: UserLogin, response: Response):
    async with async_session_maker() as session:
        user = await UserRepository(session).get_one_or_none(email = data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Вы ввели неверный пароль")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}
    

@router.get('/only_auth', summary='Кому печеньку?')
async def only_auth(request: Request):
    access_token = request.cookies.get('access_token') or None

    return {"access_token": access_token}
    