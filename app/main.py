import os

from fastapi import FastAPI
from app.core.db import engine, Base
from dotenv import load_dotenv
from app.api.v1.post.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.uploads.router import router as uploads_router
from app.api.v1.tags.router import router as tags_router
from app.api.v1.categories.router import router as categories_router
from fastapi.staticfiles import StaticFiles

from app.core.middleware import register_middleware






# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder

load_dotenv()

MEDIA_DIR = "app/media"


def create_app() -> FastAPI:
    app = FastAPI(
        title="My API Blog",
        description="This is my API Blog",
        version="0.1",
        swagger_ui_parameters={"persistAuthorization": True},
    )
    Base.metadata.create_all(bind=engine) #dev database
    
    register_middleware(app)
    
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(uploads_router)
    app.include_router(tags_router)
    app.include_router(categories_router)
    
    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    

    return app

app = create_app()





