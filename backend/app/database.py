from pymongo import ASCENDING, MongoClient
from pymongo.database import Database

from app.config import get_settings

settings = get_settings()
client = MongoClient(settings.mongodb_uri)
database: Database = client[settings.mongodb_db_name]


def get_database() -> Database:
    return database


def init_db() -> None:
    database.users.create_index([('email', ASCENDING)], unique=True)
    database.chats.create_index([('user_id', ASCENDING), ('updated_at', ASCENDING)])
    database.messages.create_index([('chat_id', ASCENDING), ('created_at', ASCENDING)])
