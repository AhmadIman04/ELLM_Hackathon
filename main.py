from fastapi import FastAPI
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

app = FastAPI()

# ——— 1) Initialize Firebase Admin (do this once) ———
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ellm-hackathon-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# ——— 2) Define request model ———
class LoginRequest(BaseModel):
    patientid: int
    password: str


@app.post("/login")
async def login(req: LoginRequest):
    # 3a) Fetch patient_table
    table_ref = db.reference('patient_table')
    data = table_ref.get()

    # 3b) Convert to DataFrame (rows)
    df = pd.DataFrame(data)

    # 3c) Extract list of valid IDs
    list_id = df["PatientID"].tolist()

    # 3d) Check login
    if req.password == "123" and req.patientid in list_id:
        return {"success": True}
    else:
        return {"success": False}
    


class SignupRequest(BaseModel):
    patientid: int
    name: str
    age: int
    health_condition: str

@app.post("/signup")
async def signup(req: SignupRequest):
    # Reference to patient_table
    table_ref = db.reference('patient_table')
    data = table_ref.get()

    df = pd.DataFrame(data)

    # 3c) Extract list of valid IDs
    list_id = df["PatientID"].tolist()

    if req.patientid in list_id :
        return {"success":False, "message":"Registration Invalid"}

    # Add new patient
    new_patient = {
        "PatientID": req.patientid,
        "Patient Name": req.name,
        "Age": req.age,
        "Health Condition": req.health_condition
    }
    table_ref.push(new_patient)

    return {"success": True, "message": "Patient registered successfully!"}
    




