class BronkaException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

# general
class ObjectNotFoundException(BronkaException):
    detail = "Объект не найден"


class DateErrorException(BronkaException):
    detail = "Дата выезда должна быть позже даты заезда"

# auth
class UserAlredyExistsException(BronkaException):
    detail = "Пользователь с таким email уже существует"


# bookings
class AllRoomsAreBookedException(BronkaException):
    detail = "Не осталось свободных номеров"

