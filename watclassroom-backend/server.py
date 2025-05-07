from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os

load_dotenv()
uwaterloo_api = os.getenv("UWATERLOO_API_KEY")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/locations/{location}")
async def get_nearest_location(location: str):
    return location

@app.get("/locations")
async def get_all_locations():

    url = "https://openapi.data.uwaterloo.ca/v3/Locations"

    payload = {}
    headers = {
    'x-api-key': uwaterloo_api,
    'accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return (response.text)