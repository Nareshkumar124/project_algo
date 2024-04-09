from fastapi import FastAPI
from .routes import userRouter,videoRouter
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


# Load .env file
load_dotenv()

app=FastAPI(
    title="VideoText App",
    docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router=userRouter,
    prefix="/api"
)

app.include_router(
    router=videoRouter,
    prefix="/api"
)
