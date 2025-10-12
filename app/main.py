from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exceptions import TripNotFoundError, TripAlreadyExistsError, InvalidTripDataError
from app.travel_together.handlers import router as travel_router


app = FastAPI()

app.include_router(travel_router)


@app.exception_handler(TripNotFoundError)
async def trip_not_found_handler(request, exc: TripNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Trip not found",
            "message": str(exc),
            "trip_id": exc.trip_id
        }
    )


@app.exception_handler(TripAlreadyExistsError)
async def trip_already_exists_handler(request, exc: TripAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "Trip already exists",
            "message": str(exc),
            "trip_id": exc.trip_id
        }
    )


@app.exception_handler(InvalidTripDataError)
async def invalid_trip_data_handler(request, exc: InvalidTripDataError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid trip data",
            "message": str(exc),
            "details": exc.details
        }
    )
