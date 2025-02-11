import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import APP_HOST, APP_PORT
from fastapi.staticfiles import StaticFiles
from app.routes.publication_router import publication_router

app = FastAPI()

app.mount("/files", StaticFiles(directory="static_files"), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(publication_router, tags=["Publication APIs"])

@app.get("/")
async def root():
    return {"message": "Hello from home"}

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host=APP_HOST,
        port=APP_PORT,
        workers=4
    )
