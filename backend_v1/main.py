# main.py
# This file starts the backend server and handles requests

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from ndvi import calculate_ndvi_time_series

app = FastAPI(title="True Carbon Backend")


# -----------------------------
# Data model for farm boundary
# -----------------------------
class FarmBoundary(BaseModel):
    type: str
    coordinates: list


# -----------------------------
# NDVI API Endpoint
# -----------------------------
@app.post("/ndvi")
def get_ndvi(
    farm: FarmBoundary,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31"
):
    """
    Receives farm boundary and returns NDVI time-series
    """

    ndvi_data = calculate_ndvi_time_series(
        farm_geojson=farm.dict(),
        start_date=start_date,
        end_date=end_date
    )

    return {
        "status": "success",
        "points": len(ndvi_data),
        "ndvi_timeseries": ndvi_data
    }