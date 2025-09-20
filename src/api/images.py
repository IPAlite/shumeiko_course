from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.services.images import ImagesService
from src.tasks.tasks import resize_image

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("")
def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    image_path = ImagesService.upload_image(file)
    background_tasks.add_task(resize_image, image_path)
    resize_image.delay(image_path)
