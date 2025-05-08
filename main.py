
from fastapi import FastAPI,Query
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db 
import pandas as pd
import datetime
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from fastapi import HTTPException


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend URL like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ——— 1) Initialize Firebase Admin (do this once) ———
cred = credentials.Certificate('credentials2.json')
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
    #print(records)
    #print(df)
    #print(df.columns)
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
async def post_diet_plan(req: dietplaninput):
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

@app.put("/update_diet_plan")
async def upsert_diet_plan(req: dietplaninput):
    ref = db.reference('diet_plan_settings')

    # 1) Pull down all entries
    all_plans = ref.get() or {}

    # 2) Find the key for this patient, if it exists
    matching_key = None
    for key, plan in all_plans.items():
        # plan might be None if someone deleted it; guard against that
        if isinstance(plan, dict) and plan.get("PatientID") == req.patientid:
            matching_key = key
            break

    # 3) Prepare the data you want to write
    data_to_write = {
        "PatientID": req.patientid,
        "Target_Daily_Calories": req.targetdailycalories,
        "Max_Fat": req.max_fat,
        "Max_Sodium": req.max_sodium,
        "Max_Sugar": req.max_sugar,
        "Notes": req.Notes
    }

    # 4) Update if found, otherwise push new
    try:
        if matching_key:
            ref.child(matching_key).update(data_to_write)
            return {"success": True, "message": "Diet plan updated for patient"}
        else:
            ref.push(data_to_write)
            return {"success": True, "message": "Diet plan created for patient"}
    except Exception as e:
        # Wrap any Firebase errors in a 500
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

@app.get("/get_diet_plan")
async def get_diet_plan(patientid: int = Query(...)):
    raw = db.reference("diet_plan_settings").get()
    if isinstance(raw, dict):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        records = []

    df = pd.DataFrame(records)
    df = df[df["PatientID"] == patientid]
    return df.to_dict(orient="records")



@app.get("/get_patient_dr")
async def get_patient_by_drid(drid: int = Query(...)):
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

    latest_log_arr = []
    for i in range (len(df2)):
        patient_id = df2.iloc[i]["PatientID"]
        diet_log = db.reference('diet_logs')
        raw = diet_log.get()
        # 2) Normalize into a list of dicts
        if isinstance(raw, dict):
            records = list(raw.values())
        elif isinstance(raw, list):
            records = raw
        else:
            records = []

        # 3) Turn into DataFrame
        df_dietlog = pd.DataFrame(records)
        df_dietlog = df_dietlog[df_dietlog["PatientID"]==patient_id]
        df_dietlog["datetime"]= pd.to_datetime(df_dietlog["datetime"])
        latest_log_diet  = df_dietlog["datetime"].max()

        exercise_log = db.reference('exercise')
        raw = exercise_log.get()
        # 2) Normalize into a list of dicts
        if isinstance(raw, dict):
            records = list(raw.values())
        elif isinstance(raw, list):
            records = raw
        else:
            records = []

        df_exerciselog = pd.DataFrame(records)
        df_exerciselog = df_exerciselog[df_exerciselog["PatientID"]==patient_id]
        df_exerciselog["Datetime"]= pd.to_datetime(df_exerciselog["Datetime"])
        latest_log_exercise  = df_exerciselog["Datetime"].max()

        if(latest_log_diet>latest_log_exercise):
            latest_log_arr.append(latest_log_diet)
        else:
            latest_log_arr.append(latest_log_exercise) 

    df2["Last_Activity"]=latest_log_arr

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
    df=df[df["PatientID"]==id]
 

    df2=df.copy()

    latest_log_arr = []
    for i in range (len(df2)):
        patient_id = df2.iloc[i]["PatientID"]
        diet_log = db.reference('diet_logs')
        raw = diet_log.get()
        # 2) Normalize into a list of dicts
        if isinstance(raw, dict):
            records = list(raw.values())
        elif isinstance(raw, list):
            records = raw
        else:
            records = []

        # 3) Turn into DataFrame
        df_dietlog = pd.DataFrame(records)
        df_dietlog = df_dietlog[df_dietlog["PatientID"]==patient_id]
        df_dietlog["datetime"]= pd.to_datetime(df_dietlog["datetime"])
        latest_log_diet  = df_dietlog["datetime"].max()

        exercise_log = db.reference('exercise')
        raw = exercise_log.get()
        # 2) Normalize into a list of dicts
        if isinstance(raw, dict):
            records = list(raw.values())
        elif isinstance(raw, list):
            records = raw
        else:
            records = []

        df_exerciselog = pd.DataFrame(records)
        df_exerciselog = df_exerciselog[df_exerciselog["PatientID"]==patient_id]
        df_exerciselog["Datetime"]= pd.to_datetime(df_exerciselog["Datetime"])
        latest_log_exercise  = df_exerciselog["Datetime"].max()

        if(latest_log_diet>latest_log_exercise):
            latest_log_arr.append(latest_log_diet)
        else:
            latest_log_arr.append(latest_log_exercise) 

    df2["Last Activity"]=latest_log_arr


    if df2.empty:
        return {"error": "Patient not found"}
    
    

    return df2.iloc[0].to_dict()








    
    



    








