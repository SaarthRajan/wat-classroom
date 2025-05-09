from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os
from geopy.distance import geodesic as GD

load_dotenv()
uwaterloo_api = os.getenv("UWATERLOO_API_KEY")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/find_nearest_locations/{building_code}")
async def find_nearest_locations(building_code):

    # must ensure that the building_code is correct
    # ensure that with a checkbox

    payload = {}
    headers = {
        'x-api-key': uwaterloo_api,
        'accept': 'application/json'
    }

    url_location_code = f"https://openapi.data.uwaterloo.ca/v3/Locations/{building_code}"

    url_locations = "https://openapi.data.uwaterloo.ca/v3/Locations"

    
    cur_loc_response = requests.request("GET", url_location_code, headers=headers, data=payload)

    cur_loc_json = cur_loc_response.json()

    cur_loc = (cur_loc_json["latitude"], cur_loc_json["longitude"])
    
    loc_response = requests.request("GET", url_locations, headers=headers, data=payload)

    loc_json = loc_response.json()

    distances = {}
    
    for entry in loc_json:
        loc = entry["latitude"], entry["longitude"]
        distances[entry["buildingCode"]] = f"{GD(loc,cur_loc).m} m"

    sorted_dict = dict(sorted(distances.items(), key=lambda item: item[1]))

    return sorted_dict

@app.get("/locations")
async def get_all_locations():

    url = "https://openapi.data.uwaterloo.ca/v3/Locations"

    payload = {}
    headers = {
    'x-api-key': uwaterloo_api,
    'accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    building_list = {}

    response_json = response.json()

    for entry in response_json:
        building_list[entry["buildingCode"]] = entry["buildingName"]

    return building_list
