
from fastapi import FastAPI,Query
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db 
import pandas as pd
import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend URL like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    # 3) Check if doctor exists and password is correct
    doctor_row = df[df["Email"] == req.dremail]
    if not doctor_row.empty and req.password == "123":
        # Convert the matching row to a dictionary
        doctor_data = doctor_row.iloc[0].to_dict()
        return {"success": True, **doctor_data}
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



@app.get("/get_diet_logs")
async def get_diet_logs(patientid: int = Query(...)):
    raw = db.reference("diet_logs").get()
    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []
    df = pd.DataFrame(records)
    df = df[df["PatientID"] == patientid]
    return df.to_dict(orient="records")


@app.get("/get_exercise_logs")
async def get_exercise_logs(patientid: int = Query(...)):
    raw = db.reference("exercise").get()
    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []
    df = pd.DataFrame(records)
    df = df[df["PatientID"] == patientid]
    return df.to_dict(orient="records")



class dietplaninput(BaseModel):
    patientid: int
    targetdailycalories : int
    max_fat: int
    max_sodium : int
    max_sugar : int
    Notes: str

@app.post("/post_diet_plan")
async def signup_doctor(req: dietplaninput):
    table_ref = db.reference('diet_plan_settings')
    #raw = table_ref.get()
    new_diet_plan = {
        "PatientID":req.patientid,
        "Target_Daily_Calories":req.targetdailycalories,
        "Max_Fat":req.max_fat,
        "Max_Sodium":req.max_sodium,
        "Max_Sugar":req.max_sugar,
        "Notes": req.Notes
    }

    table_ref.push(new_diet_plan)
    return {"success": True, "message": "New Diet Plan Updated"}

@app.get("/get_patient")
async def get_exercise_logs(drid: int = Query(...)):
    raw = db.reference("dr_table").get()
    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []

    df = pd.DataFrame(records)
    df = df[df["DrID"] == drid]
    patients = df.iloc[0]["PatientIDs"]

    raw2 = db.reference("patient_table").get()

    if isinstance(raw2, dict):
        records2 = list(raw2.values())
    elif isinstance(raw2, list):
        records2 = raw2
    else:
        records2 = []

    df2 = pd.DataFrame(records2)
    df2 = df2[df2["PatientID"].isin(patients)]

    return df2.to_dict(orient="records")


@app.get("/get_patient_by_id")
async def get_patient_by_id(id: int = Query(...)):
    raw = db.reference("patient_table").get()

    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []

    df = pd.DataFrame(records)
    df = df[df["PatientID"] == id]

    if df.empty:
        return {"error": "Patient not found"}

    return df.iloc[0].to_dict()








    
    



    








