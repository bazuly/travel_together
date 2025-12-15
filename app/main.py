from fastapi import FastAPI

from app.travel_together.handlers import router as travel_router

app = FastAPI()

app.include_router(travel_router)
