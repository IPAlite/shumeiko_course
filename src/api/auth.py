from fastapi import APIRouter, HTTPException, Response,  Body

from src.config import settings
from src.schemas.users import UserRequestAdd, UserAdd, UserLogin
from src.database import async_session_maker
from src.services.auth import AuthService
from src.api.dependencies import UserIdDep, DBDep

router = APIRouter(prefix="/auth", tags=['Авторизация и аутентификация'])


@router.post('/register', summary='Регистрация пользователя')
async def user_registet(db: DBDep, data: UserRequestAdd = Body(openapi_examples={
    "1": {"summary": "Потап", "value": {
        "first_name": "Потапчик",
        "last_name": "Владонов",
        "nikname": "AlonMneVlom",
        "phone": "8800553535",
        "email": "potapvlad@gmail.com",
        "password": "111"
    }}
})):
    hashed_password = AuthService().hashed_password(password=data.password)
    new_user_data = UserAdd(first_name=data.first_name, last_name=data.last_name, nikname=data.nikname, phone=data.phone, email=data.email, hashed_password=hashed_password)
    await db.users.add(new_user_data)
    await db.commit()
    
    return {'status': 'ok'}


@router.post('/login', summary='Аутентификация пользователя')
async def user_login(data: UserLogin, response: Response, db: DBDep):
    user = await db.users.get_one_or_none(email = data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Вы ввели неверный пароль")
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}
    

@router.get('/me', summary='Проверка авторизованного пользователя')
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.post('/logout', summary='Выход из системы')
async def user_logout(response: Response):
    response.delete_cookie(key = 'access_token')
    return {'status': "ok"}


@router.delete('/delete/{user_mail}', summary='Удаление пользователя')
async def user_delete(user_mail:str, db: DBDep):
    await db.users.delete(email=user_mail)
    await db.commit()
    return {'status': "ok"}