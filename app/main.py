from fastapi import FastAPI
from .routes import userRouter,videoRouter
from dotenv import load_dotenv


# Load .env file
load_dotenv()

app=FastAPI(
    title="VideoText App"
)

app.include_router(
    router=userRouter,
    prefix="/api"
)

app.include_router(
    router=videoRouter,
    prefix="/api"
)
