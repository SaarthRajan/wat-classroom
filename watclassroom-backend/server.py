from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/locations/{location}")
async def get_nearest_location(location):
    return location