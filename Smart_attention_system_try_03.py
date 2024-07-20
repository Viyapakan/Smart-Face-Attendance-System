import face_recognition
import cv2
import numpy as np
from datetime import datetime
import csv
import os

# Load known faces and their encodings
def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    # Provide paths to your image files
    image_paths = {
        "abdul kalam": r"E:\python projects\viyanu\pythonProject_01\.venv\Students_pics\abdhul_kalam.jpg",
        "nelson mandela": r"E:\python projects\viyanu\pythonProject_01\.venv\Students_pics\nelson_mandela.jpeg",
        "jackie chan": r"E:\python projects\viyanu\pythonProject_01\.venv\Students_pics\jackie_chan.jpg"
    }

    for name, path in image_paths.items():
        if os.path.isfile(path):
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(name)
        else:
            print(f"Image file not found at: {path}")

    return known_face_encodings, known_face_names

def mark_attendance(name, students):
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = today_date + ".csv"

    # Read the existing records to check if the person has already been marked
    records = []
    if os.path.isfile(filename):
        with open(filename, 'r', newline='') as f:
            reader = csv.reader(f)
            records = list(reader)

    # Check if the person has already been marked today
    person_marked_today = any(
        record[0] == name and record[1].startswith(today_date)
        for record in records
    )

    if not person_marked_today and name in students:
        # Add the person's attendance if they haven't been marked today
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name, datetime.now().strftime("%H:%M:%S")])
        # Remove the name from the students list
        students.remove(name)
        print(f"Attendance recorded for {name}. Remaining students: {students}")

# Load known faces
known_face_encodings, known_face_names = load_known_faces()
students = known_face_names.copy()

# Initialize webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Resize the frame for faster processing
    rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            mark_attendance(name)

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    cv2.imshow('Attendance System', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
