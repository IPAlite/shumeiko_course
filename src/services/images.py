import shutil

from src.services.base import BaseService


class ImagesService(BaseService):
    def upload_image(self, file):
        image_path = f"src/static/images/{file.filename}"
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)

        return image_path
