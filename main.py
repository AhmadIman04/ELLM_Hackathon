
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
    dremail: str
    password: str


@app.post("/login_doctor")
async def login_doctor(req: LoginRequest):
    # 3a) Fetch patient_table
    table_ref = db.reference('dr_table')
    raw = table_ref.get()

    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []

    # 3) Turn into DataFrame
    df = pd.DataFrame(records)

    # 3c) Extract list of valid IDs
    list_email = df["Email"].tolist()

    # 3d) Check login
    if req.password == "123" and req.dremail in list_email:
        return {"success": True}
    else:
        return {"success": False}
    


class SignupRequestDoctor(BaseModel):
    email : str
    name: str
    password : str


@app.post("/signup_doctor")
async def signup_doctor(req: SignupRequestDoctor):
    table_ref = db.reference('dr_table')
    raw = table_ref.get()

    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []


    # 3) Turn into DataFrame
    df = pd.DataFrame(records)
    list_email = df["Email"].tolist()

    dr_id = int(df["DrID"].max()) + 1

    if req.email in list_email :
        return {"success":False, "message":"Registration Invalid"}
    
    new_dr = {
        "DrName":req.name,
        "Email":req.email,
        "DrID":dr_id
    }

    table_ref.push(new_dr)
    return {"success": True, "message": "Doctor registered successfully!"}

    
    



    








