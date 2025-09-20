from src.utils.db_manager import DBmanager


class BaseService:
    db: DBmanager | None

    def __init__(self, db: DBmanager | None = None) -> None:
        self.db = db
