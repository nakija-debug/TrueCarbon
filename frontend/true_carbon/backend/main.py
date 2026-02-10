"""
Minimal FastAPI entrypoint (skeleton).
This file is a simple example showing where to attach auth routers.
Replace the placeholders with real fastapi-users wiring when ready.
"""
from fastapi import FastAPI

app = FastAPI(title="TRUE CARBON Backend (Skeleton)")


@app.get("/")
async def root():
    return {"message": "TRUE CARBON backend skeleton. Implement auth routes in app/"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
