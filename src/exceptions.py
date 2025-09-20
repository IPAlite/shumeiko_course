from fastapi import HTTPException


class BronkaException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


# general
class ObjectNotFoundException(BronkaException):
    detail = "Объект не найден"


class SeveralIdenticalObjects(BaseException):
    detail = "Существует несколько похожих объектов"


class DateErrorException(BronkaException):
    detail = "Дата выезда должна быть позже даты заезда"


# auth
class ObjectAlredyExistsException(BronkaException):
    detail = "Похожий объект уже существует"


# bookings
class AllRoomsAreBookedException(BronkaException):
    detail = "Не осталось свободных номеров"


class BronkaHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(BronkaHTTPException):
    staus_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(BronkaHTTPException):
    staus_code = 404
    detail = "Номер не найден"
