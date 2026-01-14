import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from config import APP_HOST, APP_PORT
from app.core.logger import logger
from app.core.db import (
    connect_to_mongo,
    close_mongo_connection
)
from app.routes.publication_router import publication_router
from app.routes.auth_router import auth_router
from app.routes.admin_router import admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Connecting to mongo db")
    connect_to_mongo()
    yield

    logger.warning("Closing mongo connection")
    close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, tags=["Admin auth APIs"])
app.include_router(publication_router, tags=["Publication APIs"])
app.include_router(admin_router, tags=["Admin APIs"])


@app.get("/")
async def root():
    return {"message": "Hello from home"}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,
        workers=2
    )
