# Create and Load Location Data - Run to update building data

from dotenv import load_dotenv
import requests
import os
import json

load_dotenv()
uwaterloo_api = os.getenv("UWATERLOO_API_KEY")
base_uwaterloo_url = "https://openapi.data.uwaterloo.ca/v3"


"""
get_all_locations() returns uwaterloo building locations (which are available with api). 

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
def get_all_locations() -> dict:
    url = base_uwaterloo_url + "/Locations"
    headers = {
        'x-api-key': uwaterloo_api,
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    response_json = response.json()
    building_list = {}
    for entry in response_json:
        if entry["latitude"]:
            building_list[entry["buildingCode"]] = {
                "name": entry["buildingName"],
                "latitude": entry["latitude"],
                "longitude": entry["longitude"]
            }
    return building_list

# Update the buildings.json file
if __name__ == "__main__":
    data = get_all_locations()
    with open('buildings.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("Location data saved to buildings.json")
