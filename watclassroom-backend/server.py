# import modules reqd.
from fastapi import FastAPI
from dotenv import load_dotenv
import requests
import os
from geopy.distance import geodesic as GD
import json
from datetime import datetime, timedelta
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

# to allow communicate with fronted in local
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
            "slots": "open classroom slots info"
        }
    }

Side Effects: Calls Portal API
"""
def get_buildings_with_open_classrooms() -> dict:
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
def get_empty_classes() -> dict:
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

"""
sort_by_dist(buildingCode) takes building_code and empty_class_data 
and sorts slots based on the nearest location

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

Side Effects: None
"""
def sort_by_dist(building_code: str, empty_class_data: dict) -> dict:

    with open('buildings.json', 'r') as f:
        buildings = json.load(f)

    if building_code not in buildings:
        raise ValueError(f"Building code '{building_code}' not found in location data.")

    cur_loc = (buildings[building_code]["latitude"], buildings[building_code]["longitude"])
    distances = {}

    for code in empty_class_data:
        if code not in buildings:
            continue

        loc = (buildings[code]["latitude"], buildings[code]["longitude"])
        dist_m = GD(cur_loc, loc).meters
        distances[code] = dist_m

    # Sort by distance ascending
    sorted_buildings = sorted(distances.items(), key=lambda item: item[1])

    sorted_empty_classes = {}
    for code, dist in sorted_buildings:
        sorted_empty_classes[code] = empty_class_data[code]

    return sorted_empty_classes

"""
filter_by_time(empty_class_data) takes empty_class_data and filters 
out all the slots that are not ongoing or wont start within one hour 
of current time. Removes all the slots that are empty and buildings
that don't have any slots. 

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

Side Effects: None
"""
def filter_by_time(empty_class_data: dict) -> dict:
    cur_dt = datetime.now()
    cutoff_dt = cur_dt + timedelta(hours=1)

    filtered_data = {}

    for building_code, rooms in empty_class_data.items():
        filtered_rooms = {}

        for room_code, slots in rooms.items():
            filtered_slots = []

            for start_str, end_str in slots:
                slot_start_dt = datetime.strptime(start_str, "%H:%M:%S").replace(
                    year=cur_dt.year, month=cur_dt.month, day=cur_dt.day)
                slot_end_dt = datetime.strptime(end_str, "%H:%M:%S").replace(
                    year=cur_dt.year, month=cur_dt.month, day=cur_dt.day)

                # Condition: slot is currently open OR starts within the next hours_ahead
                if (slot_start_dt <= cur_dt <= slot_end_dt) or (cur_dt <= slot_start_dt <= cutoff_dt):
                    filtered_slots.append([start_str, end_str])

            if filtered_slots:
                filtered_rooms[room_code] = filtered_slots

        if filtered_rooms:
            filtered_data[building_code] = filtered_rooms

    return filtered_data

"""
    GET /all_buildings

    Returns building info from local JSON for location dropdown.

    Returns:
        JSONResponse: JSON dictionary of buildings with their info.
"""
@app.get("/all_buildings")
async def get_all_buildings():
    with open('buildings.json', 'r') as f:
        buildings = json.load(f)
    return JSONResponse(content=buildings)

"""
    GET /result/{buildingCode}

    Returns result of sorted and filtered open classrooms displayed 
    in scrollview

    Returns:
        JSONResponse: JSON dictionary of buildings with their info.
"""
@app.get("/result/{buildingCode}")
async def result(buildingCode):
    classes = get_empty_classes()
    by_dist = sort_by_dist(buildingCode, classes)
    return filter_by_time(by_dist)