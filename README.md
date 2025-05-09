


# 🏥 Health Tracking System — Technical Architecture Overview

This project consists of **two main user-facing systems** connected through a shared backend and real-time database:

* 📱 **Mobile App** for Patients
* 💻 **Web Dashboard** for Doctors

Both are seamlessly synchronized via **FastAPI backend** and **Firebase Realtime Database** to ensure real-time updates across users and platforms.
AI components powered by Google’s **Gemini models** are integrated through the backend (detailed separately in the *LLM Architecture* section).

---

## 📱 Mobile App (Patients)

Built with **React Native** (supports both iOS & Android), the patient app empowers users to:

* 📊 **View daily nutritional limits** (set by their doctor)
* 📸 **Upload meal photos** for nutritional analysis
* 🤖 **Chat with a personalized AI assistant**
* 🚶‍♂️ **Track daily physical activity** via built-in step tracker

### 🥗 Meal Tracking Flow:

1. Patient captures a meal photo in the app.
2. Image is uploaded to the backend for analysis.
3. Estimated nutritional data (calories, sugar, fat, sodium) is processed and stored in Firebase.
4. Real-time updates are sent back to both the patient app and doctor dashboard.

### 🚶‍♀️ Activity Tracking:

* The step tracker counts daily steps ➜ converts to distance and **calories burned**.
* Synced instantly to Firebase so doctors can monitor patient activity in real time.

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


