# Backend for WatClassroom

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
