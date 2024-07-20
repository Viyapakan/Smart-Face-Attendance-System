# Import necessary libraries
import face_recognition  # Library for face recognition
import cv2  # OpenCV library for image and video processing
import numpy as np  # NumPy for numerical operations (not directly used here)
from datetime import datetime  # To handle date and time
import pandas as pd  # For handling Excel files
import os  # For interacting with the operating system

# Function to load known faces and their encodings
def load_known_faces():
    known_face_encodings = []  # List to store face encodings
    known_face_names = []  # List to store names associated with face encodings
    # Dictionary to map names to image file paths
    image_paths = {
        "abdul kalam": r"E:\python projects\viyanu\pythonProject_01\.venv\Students_pics\abdhul_kalam.jpg",
        "nelson mandela": r"E:\python projects\viyanu\pythonProject_01\.venv\Students_pics\nelson_mandela.jpeg",
        "jackie chan": r"E:\python projects\viyanu\pythonProject_01\.venv\Students_pics\jackie_chan.jpg"
    }

    # Loop through the image paths to load face encodings
    for name, path in image_paths.items():
        if os.path.isfile(path):  # Check if the image file exists
            image = face_recognition.load_image_file(path)  # Load the image file
            encoding = face_recognition.face_encodings(image)[0]  # Get the face encoding for the image
            known_face_encodings.append(encoding)  # Add the encoding to the list
            known_face_names.append(name)  # Add the name to the list
        else:
            print(f"Image file not found at: {path}")  # Print an error message if the file is not found

    return known_face_encodings, known_face_names, image_paths  # Return the lists of encodings, names, and paths

# Function to mark attendance in an Excel file
def mark_attendance(name, students):
    today_date = datetime.now().strftime("%Y-%m-%d")  # Get today's date
    filename = today_date + ".xlsx"  # Create a filename based on today's date

    if os.path.isfile(filename):  # Check if the Excel file already exists
        df = pd.read_excel(filename, engine='openpyxl')  # Read the existing Excel file into a DataFrame
    else:
        df = pd.DataFrame(columns=["Name", "Time"])  # Create a new DataFrame with columns for Name and Time

    # Check if the person has been marked as present today
    person_marked_today = any(
        (df['Name'] == name) & (df['Time'].str.startswith(today_date))
    )

    if not person_marked_today and name in students:  # If not marked today and the name is in the list
        new_entry = pd.DataFrame([[name, datetime.now().strftime("%H:%M:%S")]], columns=["Name", "Time"])  # Create a new entry
        df = pd.concat([df, new_entry], ignore_index=True)  # Add the new entry to the DataFrame
        df.to_excel(filename, index=False, engine='openpyxl')  # Save the updated DataFrame to the Excel file
        students.remove(name)  # Remove the name from the list of students
        print(f"Attendance recorded for {name}. Remaining students: {students}")  # Print confirmation message

# Function to display an image with a text overlay
def display_image_with_text(image_path, text):
    image = cv2.imread(image_path)  # Read the image from the given path
    if image is not None:  # Check if the image is loaded successfully
        font = cv2.FONT_HERSHEY_SIMPLEX  # Define the font
        font_scale = 1  # Define the font scale
        font_color = (255, 255, 255)  # White color for the text
        thickness = 2  # Thickness of the text
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]  # Get the size of the text
        text_x = (image.shape[1] - text_size[0]) // 2  # Calculate the x position to center the text
        text_y = (image.shape[0] + text_size[1]) // 2  # Calculate the y position to center the text
        cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, thickness)  # Overlay the text on the image

        cv2.imshow('Detected Person', image)  # Display the image in a window
        cv2.waitKey(3000)  # Wait for 3 seconds
        cv2.destroyAllWindows()  # Close the window
    else:
        print("Image not found.")  # Print an error message if the image cannot be loaded

# Load known faces and image paths
known_face_encodings, known_face_names, image_paths = load_known_faces()

# Initialize the webcam
video_capture = cv2.VideoCapture(0)

# Track the current day to reset the students list at the beginning of each day
current_day = datetime.now().strftime("%Y-%m-%d")
students = known_face_names.copy()  # Create a copy of the list of known face names

# Start capturing video from the webcam
while True:
    ret, frame = video_capture.read()  # Capture a frame from the video feed
    if not ret:  # Break the loop if frame capture fails
        break

    rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB color space
    face_locations = face_recognition.face_locations(rgb_small_frame)  # Find face locations in the frame
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)  # Get face encodings for the detected faces

    # Iterate over the detected faces
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)  # Compare detected face with known faces
        name = "Unknown"  # Default name if no match is found

        if True in matches:  # If there is a match
            first_match_index = matches.index(True)  # Get the index of the first match
            name = known_face_names[first_match_index]  # Retrieve the name associated with the match
            mark_attendance(name, students)  # Mark attendance for the detected person
            image_path = image_paths.get(name)  # Get the image path for the detected person
            if image_path:  # If an image path is found
                current_time = datetime.now()  # Get the current time
                hour = current_time.hour  # Get the current hour
                # Create a personalized greeting message based on the time of day
                if hour < 12:
                    greeting_text = f"Good Morning {name}, have a great day!"
                else:
                    greeting_text = f"Good Afternoon {name}!"
                display_image_with_text(image_path, greeting_text)  # Display the image with the greeting text

    today_day = datetime.now().strftime("%Y-%m-%d")  # Get today's date
    if today_day != current_day:  # If the day has changed
        current_day = today_day  # Update the current day
        students = known_face_names.copy()  # Reset the list of students

    cv2.imshow('Attendance System', frame)  # Display the video feed in a window

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Check if the 'q' key is pressed
        break  # Exit the loop

# Release the webcam and close all OpenCV windows
video_capture.release()
cv2.destroyAllWindows()
