


# 🏥 Stellgin 

This project consists of **two main user-facing systems** connected through a shared backend and real-time database:

* 📱 **Mobile App** for Patients
* 💻 **Web Dashboard** for Doctors

Both are seamlessly synchronized via **FastAPI backend** and **Firebase Realtime Database** to ensure real-time updates across users and platforms.
AI components powered by Google’s **Gemini models** are integrated through the backend (detailed separately in the *LLM Architecture* section).

---

## 📱 Mobile App (Patients)

Built with **React Native** (iOS & Android), the patient app empowers users to:

- 📊 **View daily nutritional limits** (set by their doctor)  
- 📸 **Upload meal photos** for nutritional analysis  
- 🤖 **Chat with a personalized AI assistant**  
- 🚶‍♂️ **Track daily physical activity** via built-in step tracker
- 📈 **Real-Time Dashboard Flow**

---

### 📊 View Daily Nutritional Limits Flow

1. **Doctor configures limits**  
   In the doctor’s dashboard, the physician sets or adjusts the patient’s daily targets for calories, sugar, fat, and sodium.  
2. **Firebase sync**  
   Limits are pushed instantly to Firebase Realtime Database.  
3. **App fetches limits**  
   On launch—or whenever they change—the mobile app retrieves the latest targets.  
4. **Display in UI**  
   The patient sees these limits on the home screen, with progress bars for each nutrient.  


---
---

### 📸 Upload Meal Photos for Nutritional Analysis Flow

1. **Launch picker**  
   User taps the food log section to open the camera or gallery.  
2. **Preprocess on-device**  
   Image is resized/compressed for optimal upload.  
3. **Secure upload**  
   Sent via FastAPI with authentication tokens.  
4. **Backend AI call**  
   Gemini processes the image and returns nutritional estimates.  
5. **Write to Firebase**  
   Results are stored under the patient’s record.  
6. **Update UI & history**  
   App displays values and logs the meal in the consumption history.

---

### 🤖 Chat with a Personalized AI Assistant Flow

1. **Open chat**  
   Tap the AI chatbot icon to launch the AI assistant.  
2. **Send query**  
   Type a question (e.g. “What should i eat for dinner?”) .  
3. **Route to backend**  
   FastAPI forwards the message plus patient context to Gemini.  
4. **Receive response**  
   Gemini returns tailored advice or suggestions.  

---

### 🚶‍♀️ Activity Tracking Flow

1. **Count steps**  
   Built-in tracker tallies daily steps.  
2. **Convert metrics**  
   Steps → distance → estimated calories burned.  
3. **Sync to Firebase**  
   Activity data is pushed in real time.  
4. **Doctor visibility**  
   Doctors can monitor patient activity live via the web dashboard.
   

### 📈 Real-Time Dashboard Flow

1. **Initialize dashboard component**  
   - When the patient opens the dashboard section, the app initializes real-time listeners to Firestore.

2. **Subscribe to Firestore data**  
   - **Activity data:** steps, distance, calories burned  
   - **Diet data:** meal records with calories, sugar, fat, sodium  

3. **Aggregate metrics**  
   - Compute daily totals and weekly summaries for both activity and diet.


---

## 💻 Doctor's Dashboard (Web)

Built using **React (Typescript)** and **Tailwind CSS**, the doctor's dashboard acts as a control center:

* 👩‍⚕️ Monitor multiple patients simultaneously
* 📊 View real-time patient stats:

  * Cumulative daily intake (calories, sugar, fat, sodium)
  * Step counts and calories burned
* ✍️ Set or adjust each patient’s **nutritional limits**
* 💬 Leave **personalized dietary suggestions or notes** that sync to the patient’s app

✅ All changes are **instantly synced** via Firebase, enabling two-way communication and live tracking.

---

## 🔗 Backend Services

The **FastAPI** backend serves as the central orchestrator, connecting apps, database, and AI services.
It exposes **REST APIs** for:

* 🔒 User authentication and management (patients & doctors)
* 📥 Uploading & processing meal photos
* 🤖 Handling AI chatbot queries
* 📝 Managing nutritional limits and suggestions
* 📊 Updating patient dashboards

### 🔄 Data Flow:

* All patient health data is stored in **Firebase Realtime Database**:

  * Meal records
  * Step counts & calorie burns
  * Doctor-set nutritional goals
  * Chatbot interaction logs

Both apps use Firebase’s realtime sync ➜ providing instant, seamless updates.

---

## 🛠️ Technology Stack Summary

| Component          | Tech Stack                       |
| ------------------ | -------------------------------- |
| **Mobile App**     | React Native                     |
| **Web Dashboard**  | React (Typescript), Tailwind CSS |
| **Backend**        | FastAPI (Python)                 |
| **Database**       | Firebase Realtime Database       |
| **AI Integration** | Gemini APIs (via Backend)        |



## 🤖 LLM Architecture Overview

AI functionality in this system is divided into **two core tasks**:  
- 🥗 **Meal Analysis** (using multimodal input)  
- 💬 **Personalized Chatbot Interactions**  

Both are powered by **Google’s Gemini models** and integrated through the FastAPI backend, which handles context building and API communication.

---

### 🥗 Meal Analysis (Multimodal Inference Flow)

1. **Patient uploads meal photo**  
   The mobile app sends the image to the backend via FastAPI.  

2. **Forward to Gemini 2.0 Flash**  
   The backend calls Gemini’s multimodal model, which can analyze the image and return structured nutritional data.

3. **AI estimates nutritional values**  
   - 🔥 **Calories**  
   - 🍬 **Sugar content**  
   - 🥓 **Fat content**  
   - 🧂 **Sodium levels**  

4. **Parse and store results**  
   The backend processes the AI response and writes the estimated values into the patient’s record in **Firebase Realtime Database**.

5. **Real-time updates**  
   Both the patient’s app and doctor’s dashboard reflect the new meal data instantly, thanks to Firebase’s sync mechanism.

> ✅ This architecture hides the AI model complexity from front-end apps while keeping updates **fast** and **real-time**.

---

### 💬 Chatbot Personalization (LLM with Contextual Data Flow)

1. **Patient sends chatbot query**  
   The user types a question (e.g., "Can I have dessert today?") in the app’s chat interface.

2. **Backend gathers live patient data**  
   From Firebase, the backend fetches:  
   - 🍬 **Current consumption stats:** calories, sugar, fat, sodium  
   - 📊 **Patient's current health data**  
   - ⚙️ **Doctor-set nutritional limits**  

3. **Build enriched prompt**  
   The backend combines the user’s query with their latest health data to form a rich, context-aware prompt.

4. **Call Gemini text model API**  
   This prompt is sent to Gemini’s LLM, which returns a **personalized** and **safe** response tailored to the patient’s condition.

5. **Return and display response**  
   The chatbot reply is delivered back to the app’s chat window, ready for the user to read and act on.

> 🔒 By using real-time health data and doctor-defined limits, every chatbot reply stays **relevant** and **clinically safe** for the patient.

---

## 🛠️ Why This Design?

- **Seamless updates**: Meal data and chatbot answers reflect the patient’s **real-time health status**.
- **Scalable**: Front-end apps stay lightweight—heavy AI processing is handled server-side.
- **Safe & personalized**: AI replies always consider the patient’s latest condition and doctor’s advice.



