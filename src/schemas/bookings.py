from datetime import date

from pydantic import BaseModel, ConfigDict


class BookingAddRequest(BaseModel):
    date_from: date
    date_to: date


class BookindAdd(BaseModel):
    user_id: int
    hotel_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int


class Booking(BookindAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)
