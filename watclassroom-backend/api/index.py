# import modules reqd.
from fastapi import FastAPI, HTTPException
import os
import json

from pathlib import Path

import httpx
import aiofiles

# for logs
import logging

# for .env secrets
from dotenv import load_dotenv

# for calculating distance to sort by it
from geopy.distance import geodesic as GD

# for current time and date
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# for updating CORS Policy
from fastapi.middleware.cors import CORSMiddleware

# Model Validation
from pydantic import BaseModel, RootModel
from typing import Dict, List, Optional

# init a logger
logger = logging.getLogger("uvicorn.error")

# Pydantic Models
class BuildingInfo(BaseModel):
    name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

class AllBuildingsResponse(RootModel[Dict[str, BuildingInfo]]): pass

class EmptyClassesResponse(RootModel[Dict[str, Dict[str, List[List[str]]]]]): pass


# get api key
load_dotenv()
uwaterloo_api = os.getenv("UWATERLOO_API_KEY")

# url for requests
# base_uwaterloo_url = "https://openapi.data.uwaterloo.ca/v3"
get_open_classroom_url = "https://portalapi2.uwaterloo.ca/v2/map/OpenClassrooms"

BASE_DIR = Path(__file__).resolve().parent.parent

# fastapi app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://watclassroom.vercel.app",  # <-- Replace with your actual deployed frontend URL
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)



# REMOVE IN PROD. - This is VERY unsecure
# to allow communicate with fronted in local

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], # allow all origins, including your Expo URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

_building_cache = None


"""
read_buildings_json() reads the buildings.json file asynchronously, parses it, and caches the data.

Returns:
    dict: Dictionary of building codes mapped to building info (name, latitude, longitude).

Format:
    {
        "buildingCode": {
            "name": "buildingName",
            "latitude": XXXXXXXXXX,
            "longitude": XXXXXXXXXX
        }
    }

Side Effects:
    Reads buildings.json from disk asynchronously.
    Caches the result in global _building_cache to avoid repeated file I/O.
    Raises HTTPException(500) if file read or JSON parsing fails.
"""
async def read_buildings_json() -> dict:
    global _building_cache
    if _building_cache is not None:
        logger.debug("Using cached building data")
        return _building_cache
    try:
        logger.info("Reading buildings.json file asynchronously")
        async with aiofiles.open(BASE_DIR / "buildings.json", mode="r") as f:
            contents = await f.read()
        buildings = json.loads(contents)
        logger.info(f"Loading buildings into cache")
        _building_cache = buildings
        logger.info(f"Loaded {len(buildings)} buildings into cache")
        return buildings
    except Exception as e:
        logger.error(f"Failed to load buildings.json: {e}")
        raise HTTPException(status_code=500, detail="Failed to load buildings data")


"""
get_buildings_with_open_classrooms() fetches building data that support open classrooms from an external API.

Returns:
    dict: Mapping of building codes to a dictionary containing building name and open classroom slots info.

Format:
    {
        "buildingCode": {
            "name": "buildingName",
            "slots": "open classroom slots info"
        }
    }

Side Effects:
    Calls external Portal API.
    Raises HTTPException(502) if API call or response parsing fails.
"""
async def get_buildings_with_open_classrooms() -> dict:
    logger.info("Fetching open classrooms from external API")
    async with httpx.AsyncClient() as client:
        response = await client.get(get_open_classroom_url)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch data from external API - Status code: {response.status_code}")
        raise HTTPException(status_code=502, detail="Failed to fetch data from the API")

    try:
        result = response.json()
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from API response")
        raise HTTPException(status_code=502, detail="Invalid JSON from external API")
    
    features = result["data"]["features"]
    logger.info(f"Received {len(features)} features from API")

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
                    logger.warning(f"Invalid openClassroomSlots JSON for building {building_code}")
                    props["openClassroomSlots"] = None
        
            building_data[building_code] = {
                "name": building_name,
                "slots": props["openClassroomSlots"]
            }

    logger.info(f"Filtered {len(building_data)} buildings that support open classrooms")
    return building_data


"""
get_empty_classes() returns a dictionary of open classroom slots divided by buildings and rooms.

Returns:
    dict: Nested dictionary mapping building codes to room codes to lists of open time slots 

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

Side Effects:
    Calls get_buildings_with_open_classrooms() which may call an external API.
"""
async def get_empty_classes() -> dict:
    logger.info("Getting empty classes")
    building_data = await get_buildings_with_open_classrooms()
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

    logger.info(f"Extracted empty classes from {len(data)} buildings")
    return data


"""
sort_by_dist(building_code, empty_class_data) sorts the empty classroom data by proximity 
to the specified building code.

Args:
    building_code (str): The building code to measure distance from.
    empty_class_data (dict): Dictionary of empty classes to sort.

Returns:
    dict: A new dictionary of empty classes sorted by distance ascending from the given building.

Raises:
    ValueError: If building_code not found in location data.

Side Effects:
    Reads building location data via read_buildings_json().
"""
async def sort_by_dist(building_code: str, empty_class_data: dict) -> dict:

    logger.info(f"Sorting buildings by distance from {building_code}")
    buildings = await read_buildings_json()

    if building_code not in buildings:
        logger.error(f"Building code '{building_code}' not found in buildings data")
        raise ValueError(f"Building code '{building_code}' not found in location data.")

    cur_loc = (buildings[building_code]["latitude"], buildings[building_code]["longitude"])
    distances = {}

    for code in empty_class_data:
        if code not in buildings:
            logger.warning(f"Skipping building code {code} - not found in buildings data")
            continue

        loc = (buildings[code]["latitude"], buildings[code]["longitude"])
        dist_m = GD(cur_loc, loc).meters
        distances[code] = dist_m

    # Sort by distance ascending
    sorted_buildings = sorted(distances.items(), key=lambda item: item[1])

    sorted_empty_classes = {}
    for code, dist in sorted_buildings:
        sorted_empty_classes[code] = empty_class_data[code]

    logger.info(f"Sorted {len(sorted_empty_classes)} buildings by proximity")
    return sorted_empty_classes


"""
filter_by_time(empty_class_data) filters out open classroom slots that are not ongoing or 
will not start within the next hour.

Args:
    empty_class_data (dict): Dictionary of empty classroom slots to filter.

Returns:
    dict: Filtered dictionary containing only slots currently open or starting within one hour.

Side Effects:
    None
"""
def filter_by_time(empty_class_data: dict) -> dict:

    logger.info("Filtering empty classes by time")

    ET = ZoneInfo("America/Toronto")
    cur_dt = datetime.now(ET)
    cutoff_dt = cur_dt + timedelta(hours=1)

    filtered_data = {}

    for building_code, rooms in empty_class_data.items():
        filtered_rooms = {}

        for room_code, slots in rooms.items():
            filtered_slots = []

            for start_str, end_str in slots:
                slot_start_dt = datetime.strptime(start_str, "%H:%M:%S").replace(
                    year=cur_dt.year, month=cur_dt.month, day=cur_dt.day, tzinfo=ET)
                slot_end_dt = datetime.strptime(end_str, "%H:%M:%S").replace(
                    year=cur_dt.year, month=cur_dt.month, day=cur_dt.day, tzinfo=ET)

                # slot is currently open OR starts within the next hours_ahead
                if (slot_start_dt <= cur_dt <= slot_end_dt) or (cur_dt <= slot_start_dt <= cutoff_dt):
                    filtered_slots.append([start_str, end_str])

            if filtered_slots:
                filtered_rooms[room_code] = filtered_slots

        if filtered_rooms:
            filtered_data[building_code] = filtered_rooms

    logger.info(f"Filtered down to {len(filtered_data)} buildings with upcoming or ongoing slots")
    return filtered_data

"""
GET /all_buildings endpoint handler.

Returns:
    dict: All building codes with their names and coordinates, loaded from local JSON.

Side Effects:
    Calls read_buildings_json() which reads/caches data from disk.
"""
@app.get(
            "/all_buildings", 
            response_model=AllBuildingsResponse, 
            response_description="List of buildings with name and coordinates",
            summary="Get All Buildings",
            description="Returns a dictionary of building codes with their names and coordinates for dropdowns.",
            tags=["Buildings"],
            status_code=200,
            responses={
                500: {"description": "Internal Server Error while loading buildings.json"}
            }
        )
async def get_all_buildings():
    logger.info("GET /all_buildings called")
    return await read_buildings_json()
    

"""
GET /result/{buildingCode} endpoint handler.

Args:
    buildingCode (str): Building code to filter and sort classrooms by proximity.

Returns:
    dict: Filtered and sorted dictionary of open classroom slots near the specified building.

Raises:
    HTTPException(400): If building code is invalid.
    HTTPException(500): On unexpected server errors.

Side Effects:
    Calls get_empty_classes(), sort_by_dist(), and filter_by_time().
"""
@app.get("/result/{buildingCode}", 
            response_model=EmptyClassesResponse,
            response_description="Filtered open classroom slots sorted by proximity.",
            summary="Get Nearby Open Classrooms",
            description=(
                "Returns a list of available classrooms that are either currently empty "
                "or will be empty within the next hour. The results are filtered by time "
                "and sorted by distance from the given building code."
            ),
            tags=["Classrooms"],
            status_code=200,
            responses={
                400: {"description": "Invalid building code"},
            }
        )
async def result(buildingCode: str):
    logger.info(f"GET /result/{buildingCode} called")
    try:
        classes = await get_empty_classes()
        by_dist = await sort_by_dist(buildingCode, classes)
        filtered = filter_by_time(by_dist)
        return filtered
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected server error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")

    # return get_empty_classes() # for testing purposes

