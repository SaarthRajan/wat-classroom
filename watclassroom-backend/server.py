# import modules required
from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os
from geopy.distance import geodesic as GD
import json
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# get api key
load_dotenv()
uwaterloo_api = os.getenv("UWATERLOO_API_KEY")

# url for requests
base_uwaterloo_url = "https://openapi.data.uwaterloo.ca/v3"
get_open_classroom_url = "https://portalapi2.uwaterloo.ca/v2/map/OpenClassrooms"

# fastapi app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins, including your Expo URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    return data
        
    # return [datetime.now().strftime("%H:%M:%S"), data] 
    # debug purpose - returns an array with current time and list of open classroom slots divided by buildings

"""
sort_by_dist(buildingCode) takes buildingCode and sorts slots based on the nearest location
"""
def sort_by_dist(buildingCode):

    return {}
    

@app.get("/")
async def root():
    # return get_buildings_with_open_classrooms()
    return get_empty_classes()



@app.get("/all_buildings")
async def get_all_buildings():
    with open('buildings.json', 'r') as f:
        buildings = json.load(f)
    return JSONResponse(content=buildings)