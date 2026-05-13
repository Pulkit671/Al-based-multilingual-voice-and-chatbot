from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routes.auth import router as auth_router
from app.routes.chats import router as chats_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=upload_dir.parent), name='uploads')


@app.on_event('startup')
def startup_event() -> None:
    init_db()


@app.get('/health')
def health_check():
    return {'status': 'ok', 'service': settings.app_name}


app.include_router(auth_router)
app.include_router(chats_router)
