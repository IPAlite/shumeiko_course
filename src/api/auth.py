from fastapi import APIRouter, Response, Body

from src.schemas.users import UserRequestAdd, UserLogin
from src.services.auth import AuthService
from src.api.dependencies import UserIdDep, DBDep

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.get("/me", summary="Проверка авторизованного пользователя")
async def get_me(user_id: UserIdDep, db: DBDep):
    user = await AuthService(db).get_me(user_id)
    return {"status": "ok", "data": user}


@router.post("/register", summary="Регистрация пользователя")
async def user_registet(
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Потап",
                "value": {
                    "first_name": "Потапчик",
                    "last_name": "Владонов",
                    "nikname": "AlonMneVlom",
                    "phone": "8800553535",
                    "email": "potapvlad@gmail.com",
                    "password": "111",
                },
            }
        }
    ),
):
    await AuthService(db).user_register(data)
    return {"status": "ok"}


@router.post("/login", summary="Аутентификация пользователя")
async def user_login(data: UserLogin, response: Response, db: DBDep):
    access_token = await AuthService(db).user_login(data, response)
    return {"access_token": access_token}


@router.post("/logout", summary="Выход из системы")
async def user_logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"status": "ok"}


@router.delete("/delete/{user_mail}", summary="Удаление пользователя")
async def user_delete(user_mail: str, db: DBDep):
    await AuthService(db).user_delete(user_mail)
    return {"status": "ok"}
