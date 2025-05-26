# import modules required
from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os
from geopy.distance import geodesic as GD
import json
from datetime import datetime

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
def get_all_locations():
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
            "latitude": XXXXX,
            "longitude": XXXXX,
            "slots": "open classroom slots info"
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
                "latitude": feature["geometry"]["coordinates"][1],
                "longitude": feature["geometry"]["coordinates"][0],
                "slots": props["openClassroomSlots"]
            }
    return building_data

"""
get_empty_classes() returns a dictionary of open class slots divided buildings
Format: 
    {
        "buildingCode": {
            "roomNumber": [
                [
                    "startTime", 
                    "endTime"
                ]
            ]
        }
    }

Side Effects: Calls external functions which may call an API
"""
def get_empty_classes():
    building_data = get_buildings_with_open_classrooms()
    data = {}

    for building_code, building_info in building_data.items():
        data[building_code] = {}

        if isinstance(building_info, str):
            building_info = json.loads(building_info)

        slots = building_info.get("slots", {})
        if isinstance(slots, str):
            slots = json.loads(slots)
        
        rooms = slots.get("data", [])
    
        for room in rooms:
            room_number = room.get("roomNumber")
            schedule = room.get("Schedule", [])
            
            data[building_code][f"{building_code}{room_number}"] = []

            for slot in (schedule[0]).get("Slots", []):
                start = slot.get("StartTime")
                end = slot.get("EndTime")
                (data[building_code][f"{building_code}{room_number}"]).append([f"{start}", f"{end}"])
        
    return [datetime.now().strftime("%H:%M:%S"), data] 
    # debug purpose - returns an array with current time and list of open classroom slots divided by buildings
    # this will be changed later based on the use case





    

@app.get("/")
async def root():
    # return get_all_locations()
    # return get_buildings_with_open_classrooms()
    return get_empty_classes()

