import os
import requests
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import PIL.Image # For image handling with Gemini Vision
import io
import firebase_admin
from firebase_admin import db,credentials
import pandas as pd
import re
import json
from datetime import datetime, date

# Load environment variables (optional, but good practice for API keys)
load_dotenv()


genai.configure(api_key="AIzaSyBAn6JnA-xS1OykCuJ7UDMkEIFHAd-_iyE")

# --- Initialize Gemini Models ---
# For text-only chat
text_model = genai.GenerativeModel('gemini-2.0-flash')
chat_session = text_model.start_chat(history=[]) # Maintain chat history for context

# For image understanding

# --- FastAPI App ---

# --- CORS Middleware (allow your React Native app to connect) ---
# Replace "http://localhost:19006" or your Expo Go URL if different
# For development, "*" is often used, but be more specific in production.


# --- Pydantic Models for Request/Response ---
class ChatMessage(BaseModel):
    message: str

class AIResponse(BaseModel):
    message: str
    
class ImageAIResponse(BaseModel):
    message: str
    original_filename: str

class Content(BaseModel):
  food: str
  calories_kcal: str
  sugar_g: str
  fat_g: str
  sodium_g: str

class LoginRequest(BaseModel):
    email: str
    password: str




app = FastAPI()

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ellm-hackathon-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Or restrict to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Gemini Chatbot API is running!"}

@app.post("/chat", response_model=AIResponse)
async def handle_chat(chat_message: ChatMessage):
    try:
        print(f"Received message: {chat_message.message}")
        # Send message to Gemini and get response
        # Using chat_session to maintain context
        response = chat_session.send_message(chat_message.message)
        print(f"Gemini response: {response.text}")
        return AIResponse(message=response.text)
    except Exception as e:
        print(f"Error during chat: {e}")
        # You might want to check for specific Gemini API errors here
        # For example, if response.prompt_feedback indicates blocking
        if hasattr(e, 'prompt_feedback') and e.prompt_feedback.block_reason:
             return AIResponse(message=f"Content blocked: {e.prompt_feedback.block_reason.name}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
    

@app.post("/upload-image")
async def upload_image(
    patientid : int,
    file: UploadFile = File(...)
    #prompt: str = Form("Analyze the image and format answer in the following json format:Food,calories(kcal), fat(g), sodium(g), sugar(g)") # Optional prompt from frontend
):
    try:
        #print(f"Received image: {file.filename}, prompt: {prompt}")
        IMGUR_CLIENT_ID = "a88f57f1c0bc4fd"
        IMGUR_UPLOAD_ENDPOINT = "https://api.imgur.com/3/image"

        contents = await file.read()
        
        # Prepare image for Gemini Vision
        img = PIL.Image.open(io.BytesIO(contents))

        prompt = f"""
            Analyze the image and format answer in the following json format:
            Food,calories(kcal), fat(g), sodium(g), sugar(g)
            your response should only be the json and nothing else

        """
        
        prompt_parts = [prompt, img]

        response = text_model.generate_content(prompt_parts)
        answer = response.text
        answer = re.sub(r'```json', '', answer)
        answer = re.sub(r'```', '', answer)
        answer_json = json.loads(answer)
        #print(f"{answer_json}")

        headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        resp = requests.post(
            IMGUR_UPLOAD_ENDPOINT,
            headers=headers,
            files={"image": contents}
        )
        resp.raise_for_status()
        image_link = resp.json()["data"]["link"]
        answer_json["image_link"] = image_link

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S") 

        table_ref = db.reference('diet_logs')
        raw = table_ref.get()
        
        new_diet_log = {
            "PatientID":patientid,
            "calorie_intake":answer_json["calories(kcal)"],
            "datetime":dt_string,
            "fat_intake":answer_json["fat(g)"],
            "imagelink":image_link,
            "notes":answer_json["Food"],
            "sodium_intake":answer_json["sodium(g)"],
            "sugar_intake":answer_json["sugar(g)"]
        }

        table_ref.push(new_diet_log)

        return answer_json
    
    except Exception as e:
        print(f"Error during image processing: {e}")
        if hasattr(e, 'prompt_feedback') and e.prompt_feedback.block_reason:
             return ImageAIResponse(message=f"Content blocked: {e.prompt_feedback.block_reason.name}", original_filename=file.filename or "unknown")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.post("/upload_image_and_ask", response_model=ImageAIResponse)
async def upload_image_and_ask(
    prompt: str ,
    file: UploadFile = File(...)
):
    try:
        print(f"Received image: {file.filename}, prompt: {prompt}")
        contents = await file.read()
        
        # Prepare image for Gemini Vision
        img = PIL.Image.open(io.BytesIO(contents))
        
        prompt_parts = [prompt, img]

        response = text_model.generate_content(prompt_parts,
                                               generation_config={
        "response_mime_type": "application/json",
    }
                                               )
        
        print(f"Gemini vision response: {response.text}")
        return ImageAIResponse(message=response.text, original_filename=file.filename)
    except Exception as e:
        print(f"Error during image processing: {e}")
        if hasattr(e, 'prompt_feedback') and e.prompt_feedback.block_reason:
             return ImageAIResponse(message=f"Content blocked: {e.prompt_feedback.block_reason.name}", original_filename=file.filename or "unknown")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# --- (Optional) Endpoint to reset chat history ---
@app.post("/reset-chat")
async def reset_chat_history():
    global chat_session
    chat_session = text_model.start_chat(history=[])
    return {"message": "Chat history has been reset."}

@app.get("/get-data")
async def get_data():
    try:
        patient_ref = db.reference('patient_intake')

        all_intakes = patient_ref.get()
        
        return all_intakes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing get_data: {str(e)}")

@app.post("/login_patient")
async def login_patient(req: LoginRequest):

    # 3a) Fetch patient_table
    table_ref = db.reference('patient_table')
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
    patient_row = df[df["Email"] == req.email]
    if not patient_row.empty and req.password == "123":
        # Convert the matching row to a dictionary
        patient_data = patient_row.iloc[0].to_dict()
        return {"success": True, **patient_data}
    else:
        return {"success": False}
    


class SignUpPatient(BaseModel):
    age: int
    email : str
    name: str
    password : str


@app.post("/signup_pat")
async def signup_pat(req: SignUpPatient):
    table_ref = db.reference('patient_table')
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

    pat_id = int(df["PatientID"].max()) + 1

    if req.email in list_email :
        return {"success":False, "message":"Registration Invalid"}
  
    new_pat = {
    "Age":req.age,
    "Email":req.email,
    "HealthCondition":"",
    "PatientName":req.name,
    "PatientID":pat_id,
    "patient_status":""
    }

        

    table_ref.push(new_pat)
    return {"success": True, "message": "Patient registered successfully!"}

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