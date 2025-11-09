from fastapi import FastAPI
from app.routers import files, users
from app import models
from app.database import engine
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .logging_config import setup_logging

setup_logging()

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(users.router, prefix="/users", tags=["users"])

app.mount("/static", StaticFiles(directory="frontend"), name ="static")

@app.get(
    "/", 
    response_class=HTMLResponse
)
async def read_login_page():
    try:
        with open("frontend/login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Login page not found</h1>", status_code=404)