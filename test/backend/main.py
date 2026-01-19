from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.api import router

app = FastAPI(title="Smart Exam Grading System API", version="1.0.0")

# CORS config
origins = [
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router.api_router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")


@app.get("/")
def read_root():
    return {"message": "Smart Exam Grading API is running"}
