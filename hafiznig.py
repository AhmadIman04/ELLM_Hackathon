import firebase_admin
from firebase_admin import db,credentials
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ellm-hackathon-default-rtdb.asia-southeast1.firebasedatabase.app/'  # replace with your DB URL
})

# 2) Get a reference to the 'patient_intake' node
patient_ref = db.reference('patient_intake')

# 3) Read all data under that node
all_intakes = patient_ref.get()

print(all_intakes)

