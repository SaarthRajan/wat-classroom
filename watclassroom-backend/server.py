# import modules required
from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os
from geopy.distance import geodesic as GD
import json

# get api key
load_dotenv()
uwaterloo_api = os.getenv("UWATERLOO_API_KEY")

# url for requests
base_uwaterloo_url = "https://openapi.data.uwaterloo.ca/v3"
get_open_classroom_url = "https://portalapi2.uwaterloo.ca/v2/map/OpenClassrooms"

# fastapi app
app = FastAPI()

"""
get_all_locations() returns uwaterloo building locations (which are available). 
Return Format:
    {
        "buildingCode": {
            "name": "buildingName",
            "latitude": XXXXX,
            "longitude": XXXXX
        }
    }
Side Effects: calls UWaterloo API
"""
def get_all_locations() -> dict[str, dict[str, str]]:
    url = base_uwaterloo_url + "/Locations"
    payload = {}
    headers = {
    'x-api-key': uwaterloo_api,
    'accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    building_list = {}
    response_json = response.json()

    for entry in response_json:
        if (entry["latitude"]):
            building_list[entry["buildingCode"]] = {
                "name": entry["buildingName"],
                "latitude": entry["latitude"],
                "longitude": entry["longitude"]
            }
    return building_list

"""
get_buildings_with_open_classrooms() returns the data of buildings that support empty classrooms. 
Format:
    {
        "buildingCode": {
            "name": "buildingName",
            "slots": "open classroom slots info",
            "latitude": XXXXX,
            "longitude": XXXXX
        }
    }
Side Effects: Calls Portal API
"""
def get_buildings_with_open_classrooms():
    payload = {}
    headers = {}
    response = requests.request("GET", get_open_classroom_url, headers=headers, data=payload)  
    if response.status_code != 200:
        return {"error": "Failed to fetch data from API"}  
    result = response.json()
    
    features = result["data"]["features"]

    building_data = {}

    for feature in features:
        props = feature["properties"]
        building_name = props.get("buildingName")
        building_code = props.get("buildingCode")
        support = props.get("supportOpenClassroom")

        if support:
            # To remove escape characters
            if isinstance(props.get("openClassroomSlots"), str):
                try:
                    props["openClassroomSlots"] = json.loads(props["openClassroomSlots"])
                except json.JSONDecodeError:
                    props["openClassroomSlots"] = None
        
            building_data[building_code] = {
                "name": building_name,
                "slots": props["openClassroomSlots"],
                "latitude": feature["geometry"]["coordinates"][1],
                "longitude": feature["geometry"]["coordinates"][0]
            }
        
    return building_data



@app.get("/")
async def root():
    return get_all_locations()
    # return get_buildings_with_open_classrooms()

