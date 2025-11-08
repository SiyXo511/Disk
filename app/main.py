from fastapi import FastAPI
from app.routers import files, users
from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"status": "API is running!"}