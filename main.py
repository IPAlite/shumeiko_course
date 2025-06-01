from fastapi import FastAPI, Query, Body
import uvicorn

app = FastAPI()

hotels = [
    {"id": 1, "title": "sochi", "name": "sochi"},
    {"id": 2, "title": "dubai", "name": "dubai"},
]

@app.get('/hotels')
def get_hotels(
    id:int | None = Query(None, description="Айди"), 
    title: str | None = Query(None, description='Название отеля')
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel['id'] != id:
            continue
        if title and hotel['title'] != title:
            continue
        hotels_.append(hotel)
    return hotels_

@app.post("/hotels")
def create_hotel(title: str = Body(embed=True)):
    global hotels
    hotels.append({
        "id": hotels[-1]['id'] + 1,
        "title": title
    })
    return {'status': 'ok'}

@app.put("/hotels/{hotel_id}")
def change_hotel_info(
    hotel_id: int,
    title: str = Body(),
    name: str = Body()
):
    global hotels
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            hotel['title'] = title
            hotel['name'] = name

            return {'status': 'ok'}
        return {'status': '404'}


@app.patch("/hotels/{hotel_id}")
def little_change_info(
    hotel_id: int,
    title: str | None = Body(None),
    name: str | None = Body(None)
):
    global hotels
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            hotel['title'] = title if title is not None or title == '' else hotel['title']
            hotel['name'] = name if name is not None or name == '' else hotel['name']
            return {'status': 'ok'}
        return {'status': '404'}



@app.delete('/hotels/{hotel_id}')
def del_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel['id'] != hotel_id]
    return {'status': 'ok'}



if __name__ == '__main__': 
    uvicorn.run("main:app", reload=True)