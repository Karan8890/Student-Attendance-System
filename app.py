from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import os
import cv2
import face_recognition
import numpy as np
import pandas as pd
from datetime import datetime
import base64

app = Flask(__name__)

# --- MySQL Configuration ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Diksha@4519",
    database="user_db"
)
cursor = db.cursor()

# --- Face Recognition Setup ---
KNOWN_DIR = 'dataset'
ATTENDANCE_FILE = 'attendance.csv'

known_encodings = []
known_names = []

for filename in os.listdir(KNOWN_DIR):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join(KNOWN_DIR, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0]
            known_names.append(name)

# --- Attendance Marking ---
def mark_attendance(name):
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    date_str = now.strftime('%Y-%m-%d')
    entry = {'Name': name, 'Date': date_str, 'Time': time_str}

    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(ATTENDANCE_FILE, index=False)

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            return redirect(url_for("attendance_page"))
        else:
            error = "Invalid username or password"

    return render_template("loginpage.html", error=error)

@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html")

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance_route():
    data = request.json['image']
    img_data = base64.b64decode(data.split(',')[1])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faces_in_frame = face_recognition.face_locations(rgb_img)
    encodings_in_frame = face_recognition.face_encodings(rgb_img, faces_in_frame)

    for face_encoding in encodings_in_frame:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)

        if True in matches:
            best_match_index = np.argmin(face_distances)
            name = known_names[best_match_index]
            mark_attendance(name)
            return name + " ✅ Attendance Marked"

    return "❌ Face not recognized"

@app.route("/recent_attendance")
def recent_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
        last_entries = df.tail(5).to_dict(orient='records')
        return jsonify([{"name": row['Name'], "time": row['Time']} for row in last_entries])
    else:
        return jsonify([])

# Optional: Multiple class routes if needed
@app.route('/class6_attendance')
def class6_attendance():
    return render_template('class6_att.html')

@app.route('/class4_attendance')
def class4_attendance():
    return render_template('class4_att.html')

@app.route('/class5_attendance')
def class5_attendance():
    return render_template('class5_att.html')

@app.route('/class7_attendance')
def class7_attendance():
    return render_template('class7_att.html')

import subprocess

subprocess.run(["java", "AttendanceProcessor"])
subprocess.call(["java", "AttendanceProcessor"])

# --- Run ---
if __name__ == "__main__":
    app.run(debug=True)
