# WatClassroom Backend

This is the backend API server for **WatClassroom**, a service providing real-time data on available classrooms at University of Waterloo. Built with **FastAPI**, it fetches building data and open classroom slots, then serves filtered, sorted results based on time and proximity.

---

## Prerequisites

- UWaterloo API key (get it [here](https://uwaterloo.atlassian.net/wiki/spaces/UWAPI/pages/34025641600/Getting+Started+-+OpenAPI))

**Helpful Resources**
It's recommended to review the following before using Waterloo's OpenData API:
- [OpenAPI Documentation](https://openapi.data.uwaterloo.ca/api-docs/index.html)
- [Policy 46 - Information Management](https://uwaterloo.ca/secretariat/policies-procedures-guidelines/policies/policy-46-information-management)

---

## Setup

1. Clone the repo

```bash
git clone https://github.com/SaarthRajan/wat-classroom.git
```

2. Navigate to the backend directory 

```bash
cd watclassroom-backend
```

3. Create a virtual environment

```bash
# for MacOS or Linux
python3 -m venv venv
source venv/bin/activate
```

```bash
# for windows
python3 -m venv venv
venv\Scripts\activate
# use .\venv\Scripts\Activate.ps1 if in powershell
```

4. Install the requirements using pip.
```bash
pip install -r requirements.txt
```

5. Create a .env and enter the API Key for Waterloo OpenData
```bash
UWATERLOO_API_KEY=XXXXXXXXXXXXXXXXXXXXX
```

6. Run the FastAPI App
```bash
fastapi dev server.py
```
or alternatively
```bash
uvicorn api.index:app --reload
```

After starting the server

The API will be available at `http://localhost:8000`
You can see the documentation at `http://localhost:8000/docs`

---

## API Endpoints

You can explore and test the API using the Swagger UI:  
**https://watclassroom-api.vercel.app/docs**


### `GET` `/all_buildings`
Returns all building codes with their names and coordinates.

### `GET` `/result/{buildingCode}`
Returns available open classrooms near the specified building code, filtered by time and sorted by proximity.

---

## Project Structure

```
├── api/
│   └── index.py       # Main FastAPI app and routes
├── .gitignore         # gitignore rules for python projects
├── buildings.json     # University Building location data
├── location.py        # Script to fetch and update buildings.json
├── requirements.txt   # Python dependencies
├── vercel.json        # Vercel deployment config
├── README.md          # This file
```

---

## Deployment

This backend is configured for deployment on Vercel using vercel.json. See the [Vercel docs](https://vercel.com/docs) for details.

---

## Notes

- Keep your UWaterloo API key secure and do not commit it to version control.
- The backend uses caching to minimize repeated I/O from buildings.json.
- Open classroom data depends on UWaterloo’s Portal API availability.

---

## Contributions

Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.

---

## License
MIT License © 2025 Saarth Rajan

---

