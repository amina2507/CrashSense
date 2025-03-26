import ctypes
from datetime import datetime
import http.server
import threading
import io
import socketserver
import cv2
import time
from collections import Counter
import json
import os
import number
import urllib.parse
import cv2
import threading
from queue import Queue
import sys
import sqlite3
import requests
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from collections import Counter
import cgi
from ultralytics import YOLO
import re
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = 8000
DB_NAME = 'users.db'
DB_NAME_ = 'accidents.db'
UPLOAD_DIR = 'vehicle_collision/uploads'
MODEL_PATH = 'accident_detection_model.h5'
model = load_model(MODEL_PATH)
yolo_model = YOLO('yolov8n.pt')
yolo_severity= YOLO('severity.pt')
output_file='output.txt'
output_s_file='output_s.txt'
result_queue = Queue()




def init_db_():
    conn = sqlite3.connect(DB_NAME_)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accident_data_ (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            predicted_label TEXT,
            severity_level TEXT,
            people_count INTEGER,
            date TEXT,
            uploaded_by TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db_()


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


init_db()

def preprocess_frame(frame):
    img_array = cv2.resize(frame, (224, 224))
    img_array = image.img_to_array(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array

def predict_frame(model, frame):
    processed_frame = preprocess_frame(frame)
    prediction = model.predict(processed_frame)
    print("prediction probability for detected as accident ",prediction)
    return "Accident" if prediction < 0.5 else "Non-Accident"



def detect_objects_and_count_people(frame, frame_counter, yolo_model, yolo_severity, username, threshold=0.5):
    accident_status = predict_frame(model, frame)

    # ✅ Skip everything if it's a Non-Accident
    if accident_status == "Non-Accident":
        print(f"Frame {frame_counter}: Accident Not Detected.")
        return frame, 0, 0, "No Accident Detected"
    results = yolo_model(frame)
    people_count = 0
    vehicle_count = 0
    max_people_count = 0
    max_vehicle_count = 0
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            class_id = int(box.cls.item())
            score = box.conf.item()
            x1, y1, x2, y2 = box.xyxy[0]

            # Detecting people
            if class_id == 0:  # Assuming class 0 is 'person'
                people_count += 1
                label = f'{yolo_model.names[class_id]}: {score:.2f}'
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Detecting vehicles
            elif class_id in [2, 3, 5]:  # Assuming classes 2, 3, 5 are vehicles (car, bus, etc.)
                vehicle_count += 1
                label = f'{yolo_model.names[class_id]}: {score:.2f}'
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Track the maximum number of people and vehicles detected
        max_people_count = max(max_people_count, people_count)
        max_vehicle_count = max(max_vehicle_count, vehicle_count)

    
    
        # Pass the frame to severity prediction model if accident is detected
    severity_results = yolo_severity(frame)

            # Extract labels from severity model predictions with confidence threshold
    severity_labels = []
    for result in severity_results:
        for box in result.boxes:
            if box.conf.item() >= threshold:  # Apply confidence threshold
                severity_labels.append(int(box.cls.item()))

            # Determine the majority predicted label for severity
    if severity_labels:
        majority_class_id = Counter(severity_labels).most_common(1)[0][0]
        majority_label = "Minor Accident" if majority_class_id == 1 else "Major Accident"
        print(f"Frame {frame_counter}:")
        print(f"Number of people detected in frame: {max_people_count}")  
        print(f"Number of vehicles detected in frame: {max_vehicle_count}")  
        print(f"Majority Severity Label: {majority_label}")  
    else:
        majority_label = "No Accident Detected"  # If all detections are below the threshold
        print(f"Frame {frame_counter}: {majority_label}")
    


            # Print the counts along with severity prediction
    return frame, people_count, vehicle_count, majority_label



def save_video_analysis(predicted_label, severity_level, people_count, username):
    """
    Saves the video analysis results to the SQLite database.
    """
    conn = sqlite3.connect(DB_NAME_)
    cursor = conn.cursor()
    
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
    
    cursor.execute('''
        INSERT INTO accident_data_ (predicted_label, severity_level, people_count, date, uploaded_by) 
        VALUES (?, ?, ?, ?, ?)
    ''', (predicted_label, severity_level, people_count, date_now, username))
    
    conn.commit()
    conn.close()

    print(f"Data saved successfully for user: {username}")



def process_video(video_path, model, username):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, None, 0, 0  

    predictions = []
    annotated_frames = []
    max_people_count = 0  
    total_vehicle_count = 0 
    frame_counter = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        label = predict_frame(model, frame)  
        predictions.append(label)

        # Pass username to detect_objects_and_count_people
        annotated_frame, people_count, vehicle_count, majority_label = detect_objects_and_count_people(
            frame, frame_counter, yolo_model, yolo_severity, username
        )

        max_people_count = max(max_people_count, people_count)
        total_vehicle_count += vehicle_count
        
        annotated_frames.append(annotated_frame)
        frame_counter += 1

    cap.release()
    if not predictions:
        return None, None, 0, 0  
    
    accident_count = predictions.count("Accident")
    if accident_count > len(predictions) / 2:
        majority_vote = "Accident"
        print("*------------------------------------------------------*")
        print("Vehicle collision detection has completed")
        print("*------------------------------------------------------*")
        print(f"Email sent to nearest police station and hospital for user: {username}")
    else:
        majority_vote = "Non-Accident"
        print("*------------------------------------------------------*")
        print("Vehicle collision detection has completed")
        print("*------------------------------------------------------*")
    
    
    print("Detected as", majority_vote)

    save_video_analysis(majority_vote, majority_label, max_people_count, username)
    return majority_vote, annotated_frames, max_people_count, total_vehicle_count, majority_label




def insert_user(self, first_name, last_name, email, role, username, password):
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO users (first_name, last_name, email, role, username, password)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (first_name, last_name, email, role, username, password))
                    conn.commit()
                    conn.close()




def fetch_nearest_places(latitude, longitude):
    api_key = 'AIzaSyCjGZMcRaqX3WFFTX9fTCjfnrgRrVAsg3A'
    
    # URLs for fetching hospitals and police stations
    hospital_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=5000&type=hospital&key={api_key}'
    police_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=5000&type=police&key={api_key}'
    
    print(f"Fetching hospital data from: {hospital_url}")
    print(f"Fetching police station data from: {police_url}")
    
    try:
        # Send requests to Google's Places API
        hospital_response = requests.get(hospital_url)
        police_response = requests.get(police_url)

        if hospital_response.status_code == 200:
            hospital_data = hospital_response.json()
            nearest_hospital = hospital_data['results'][0]['name'] if hospital_data['results'] else 'No nearby hospital found'
        else:
            nearest_hospital = 'Failed to fetch hospital data'

        if police_response.status_code == 200:
            police_data = police_response.json()
            nearest_police_station = police_data['results'][0]['name'] if police_data['results'] else 'No nearby police station found'
        else:
            nearest_police_station = 'Failed to fetch police station data'

        # Return the results
        return {
            'hospital': nearest_hospital,
            'policeStation': nearest_police_station
        }

    except Exception as e:
        print(f"Error fetching places: {e}")
        return {'error': 'Failed to fetch nearby places'}




class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


    def do_OPTIONS(self):
        self.send_response(200)
        if 'Access-Control-Allow-Origin' not in self.headers:
            self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        self.end_headers()
        


    def do_GET(self):
        if self.path.startswith('/get_user_info'):
            # Parse the query parameters from the URL
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Extract the 'username' parameter
            username = query_params.get('username', [None])[0]
            print(username)
            
            if username:
                # Fetch user information from the database
                user_info = self.get_user_info(username)
                
                if user_info:
                    # Send a JSON response with user information
                    response = {
                        'first_name': user_info[0],
                        'last_name': user_info[1],
                        'email': user_info[2],
                        'role': user_info[3]
                    }
                    print(response)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    # Send a 404 response if the user was not found
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'User not found'}).encode())
            else:
                # Send a 400 response if the 'username' parameter is missing
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing "username" parameter'}).encode())   

    
        elif self.path.startswith('/get_accidents'):
            self.handle_get_accidents()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_get_accidents(self):
        conn = sqlite3.connect(DB_NAME_)
        cursor = conn.cursor()
        
        # Query to fetch all accident data from the correct table
        cursor.execute("SELECT id, predicted_label, severity_level, people_count, date, uploaded_by FROM accident_data_")
        rows = cursor.fetchall()
        
        # Fetch column names dynamically
        column_names = [description[0] for description in cursor.description]
        
        # Convert rows into a list of dictionaries
        accidents = [dict(zip(column_names, row)) for row in rows]

        # Close the database connection
        conn.close()

        # Send response as JSON
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(accidents).encode('utf-8'))

    
       
    def do_POST(self):
        if self.path == '/upload':
            
            form = cgi.FieldStorage(fp=self.rfile,
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST',
                                             'CONTENT_TYPE': self.headers['Content-Type']})

            # Extract username from the form
            username = form.getvalue('username', 'UnknownUser')  # Default to 'UnknownUser' if not provided

            if 'video' in form:
                file_item = form['video']
                video_filename = os.path.join(UPLOAD_DIR, 'uploaded_video.mp4')

                with open(video_filename, 'wb') as video_file:
                    video_file.write(file_item.file.read())

                with open(output_file, 'w'):
                    pass  

                with open(output_file, 'w') as f:
                    # Redirect standard output to the file
                    original_stdout = sys.stdout  # Save a reference to the original standard output
                    sys.stdout = f    

                    # Process the video and get predictions
                    print("*--------------------------------------------------------*")
                    print("Number plate detection has started...")
                    print("*--------------------------------------------------------*\n\n")
                    number_result, output_video_path = number.extract_text_from_video(video_filename, model_path='epoch10.pt')
                    print(number_result)
                    print("*-------------------------------------------------------------------------*")
                    print("*-------------------------------------------------------------------------*")
                    print("\n\n")
                    print("Number plate detection has finished. Starting detection for vehicle collision.")
                    print("\n\n")
                    print("*-------------------------------------------------------------------------*")
                    print("*-------------------------------------------------------------------------*")
                    print("*--------------------------------------------------------*")
                    print("Accident collision detection has started...")
                    print("*--------------------------------------------------------*\n\n")

                    # Pass username to process_video function
                    majority_result, annotated_frames, people_count, vehicle_count, majority_label = process_video(
                        output_video_path, model, username
                    )

                    if majority_result is None:
                        response = {'error': 'Prediction could not be made'}
                    else:
                        # Save annotated frames as a video
                        output_video_path = os.path.join(UPLOAD_DIR, 'annotated_video.mp4')
                        fourcc = cv2.VideoWriter_fourcc(*'acv1')   
                        height, width, _ = annotated_frames[0].shape
                        out = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))

                        for frame in annotated_frames:
                            out.write(frame)
                        out.release()
                        

                        response = {
                            'username': username,  # Include username in the response
                            'number_result': number_result,      
                            'majority_result': majority_result,
                            'people_count': people_count,
                            'vehicle_count': vehicle_count,  
                            'majority_label': majority_label,
                            'annotated_video_url': f'http://192.168.1.10:{PORT}/{output_video_path}'
                        }
                        sys.stdout = original_stdout
               
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return

            self.send_response(400)
            self.end_headers()
    


        elif self.path == '/signup':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            print(post_data)
           
            form_data = urllib.parse.parse_qs(post_data)
            first_name = form_data.get('first_name', [''])[0]
            last_name = form_data.get('last_name', [''])[0]
            email = form_data.get('email', [''])[0]
            role = form_data.get('role', [''])[0]
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]

            print(f"Received data: {first_name}, {last_name}, {email}, {role}, {username}, {password}")
            
            try:
                self.insert_user(first_name, last_name, email, role, username, password)
    
             
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                self.wfile.write(b"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Signup Successful</title>
                        <script>
                            // Show alert for successful signup
                            alert('Signup Successful!');

                            // Redirect to the login page after a short delay
                            setTimeout(function() {
                                window.location.href = 'http://localhost:8000/login.html'; 
                            }, 3000); // 3000 milliseconds = 3 seconds
                        </script>
                    </head>
                    <body>
                        <h1>Signup Successful!</h1>
                        <p>You will be redirected to the login page shortly.</p>
                        <p>If you are not redirected, <a href="http://localhost:8000/login.html">click here</a>.</p>
                    </body>
                    </html>
                """)

            except sqlite3.IntegrityError:
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b"Signup failed. Please try again.")

                                
        elif self.path == '/update_accident':
            content_length = int(self.headers['Content-Length'])
            raw_post_data = self.rfile.read(content_length).decode('utf-8')
            print("Raw POST data:", raw_post_data)  

           
            data = {}
            boundary = self.headers['Content-Type'].split("=")[1]
            parts = raw_post_data.split(f"--{boundary}") 

            for part in parts:
                part = part.strip()  # Remove leading and trailing whitespace
                if not part or part == '--':  # Skip empty parts or closing boundary
                    continue
                
                # Ensure we can split into headers and body
                try:
                    headers, body = part.split('\r\n\r\n', 1)
                except ValueError:
                    print(f"Skipping part due to split error: {part}")
                    continue
                
                # Decode headers and get the content disposition
                header_lines = headers.splitlines()  # No need to decode since it's already a string
                content_disposition = next(
                    (line for line in header_lines if line.startswith('Content-Disposition')), None
                )
                
                if content_disposition:
                    name = self.extract_name(content_disposition)
                    if name:
                        data[name] = body.strip()  # Strip whitespace for clean values

            print("Parsed data:", data)

            # Proceed to update accident data
            try:
                if self.update_accident(data):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "Record updated successfully"}).encode('utf-8'))
                    print("Record updated successfully")
                else:
                    raise ValueError("Failed to update record")
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                print(f"Error updating record: {e}")


                         

        elif self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)

            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]

            print(f"Login attempt with Username: {username}, {password}")

            role = self.validate_user(username, password)
            print(role)

            if role in ['admin', 'policeman', 'governance']:
                message = 'Login successful'
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                # Set the username in the cookie
                self.send_header('Set-Cookie', f'username={username}; Path=/')
                self.send_header('Message', message)  
                self.end_headers()
                
                # Optionally, you can provide a response body here
                self.wfile.write(f'{{"status": "success", "role": "{role}"}}'.encode('utf-8'))
            
            elif role == 'user':

                self.send_response(200)  # Ensure successful response
                self.send_header('Content-type', 'application/json')  # Set proper content type
                self.end_headers()
                self.wfile.write(f'{{"status": "success", "role": "{role}"}}'.encode('utf-8'))

            else:    
                message = 'Invalid username or password.'
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.send_header('Message', message) 
                self.end_headers()
                self.wfile.write(b'Error: Invalid username or password.')


        elif self.path == '/validate_user_':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            username = form_data.get('username', [''])[0]

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": false}')

            conn.close()
                

        elif self.path == '/update_password':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            username = form_data.get('username', [''])[0]
            new_password = form_data.get('newPassword', [''])[0]

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
            conn.commit()

            if cursor.rowcount > 0:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": false}')

            conn.close()

        elif self.path == '/update_profile':
            self.handle_update_profile()  

        elif self.path == '/delete_accident':
            content_length = int(self.headers['Content-Length'])
            raw_post_data = self.rfile.read(content_length).decode('utf-8')
            print("Raw POST data:", raw_post_data)  # Log raw POST data for debugging

            # Parse the form data
            data = {}
            boundary = self.headers['Content-Type'].split("=")[1]
            parts = raw_post_data.split(f"--{boundary}")  # Use string formatting to include the boundary

            for part in parts:
                part = part.strip()  # Remove leading and trailing whitespace
                if not part or part == '--':  # Skip empty parts or closing boundary
                    continue
                
                # Ensure we can split into headers and body
                try:
                    headers, body = part.split('\r\n\r\n', 1)
                except ValueError:
                    print(f"Skipping part due to split error: {part}")
                    continue
                
                # Decode headers and get the content disposition
                header_lines = headers.splitlines()  # No need to decode since it's already a string
                content_disposition = next(
                    (line for line in header_lines if line.startswith('Content-Disposition')), None
                )
                
                if content_disposition:
                    name = self.extract_name(content_disposition)
                    if name:
                        data[name] = body.strip()  # Strip whitespace for clean values

            # Extract the ID from parsed data
            accident_id = data.get('id', '').strip('"').strip()  # Clean up the ID
            print(f"Delete request for accident ID: {accident_id}")

            # Connect to the SQLite database
            conn = sqlite3.connect(DB_NAME_)
            cursor = conn.cursor()

            # Attempt to delete the accident from the database
            cursor.execute('DELETE FROM accident_data WHERE id = ?', (accident_id,))
            conn.commit()

            # Check if any rows were affected (deleted)
            if cursor.rowcount > 0:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"message": "Accident deleted successfully."}')
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Accident not found."}')

            # Close the database connection
            conn.close()


        elif self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse the form data
            form_data = urllib.parse.parse_qs(post_data)
            
            # Extract features and predicted severity
            features = json.loads(form_data.get('features', [''])[0])
            predicted_severity = form_data.get('predicted_severity', [''])[0]
            uploaded_by = form_data.get('uploaded_by', [''])[0]

            print(f"Received data: {features}, Predicted Severity: {predicted_severity}, Uploaded by: {uploaded_by}")
            
            # Insert the data into the database
            try:
                self.insert_data(features, predicted_severity, uploaded_by)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Success! Data has been saved.')
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Error saving data.')
                 

        elif self.path == '/fetch-nearest-places':
            print("Handling POST request for /fetch-nearest-places")

            # Get the content type and check if it's multipart/form-data
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Content-Type must be multipart/form-data'}).encode())
                return

            # Parse the form data using cgi.FieldStorage
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            )

            # Extract the fields from the form data
            latitude = form.getvalue('latitude')
            longitude = form.getvalue('longitude')
            police_email = form.getvalue('policeStationEmail')
            hospital_email = form.getvalue('hospitalEmail')

            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
            print(f"Police Email: {police_email}")
            print(f"Hospital Email: {hospital_email}")

            if latitude and longitude and police_email and hospital_email:
                
                nearest_places = fetch_nearest_places(latitude, longitude)
                print(f"Nearest Places: {nearest_places}")
        
                # Send notification emails to police and hospital
    
                self.send_email(
                                police_email, 
                                "Accident Alert",
                                f"To: {nearest_places['policeStation']}\n\n" 
                                f"An accident has occurred at location: \n"
                                f"📍 Latitude: {latitude}\n"
                                f"📍 Longitude: {longitude}\n"
                                f"Please take immediate action and dispatch personnel to the scene."
                
                               )

                self.send_email(
                               hospital_email, 
                               "Accident Alert", 
                               f"To: {nearest_places['hospital']}\n\n" 
                               f"An accident has occurred at location:\n"
                               f"📍 Latitude: {latitude}\n"
                               f"📍 Longitude: {longitude}\n"
                               f"Please prepare to receive injured individuals and dispatch an ambulance to the scene."
                               
                               )


             
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'Notifications sent'}).encode())
            else:
                # Send error response for missing fields
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())

    def extract_name(self, content_disposition):
                    """Extracts the name attribute from the Content-Disposition header."""
                    for part in content_disposition.split(';'):
                        if 'name=' in part:
                            return part.split('=')[1].strip('\"')
                    return None

    def update_accident(self, data):
        try:
            conn = sqlite3.connect(DB_NAME_)
            cursor = conn.cursor()

            # Extract necessary fields from the data dictionary
            accident_id = data.get('id')
            predicted_label = data.get('predicted_label')
            severity_level = data.get('severity_level')
            people_count = data.get('people_count')
            date = data.get('date')
            uploaded_by = data.get('uploaded_by')

            cursor.execute('''
                UPDATE accident_data_
                SET predicted_label = ?, severity_level = ?, people_count = ?, date = ?, uploaded_by = ?
                WHERE id = ?
            ''', (predicted_label, severity_level, people_count, date, uploaded_by, accident_id))

            conn.commit()
            return True
        except Exception as e:
            print("Error updating accident data:", e)  # Log the error
            return False
        finally:
            conn.close()

    

    def get_username_from_request(self):
        # Retrieve the username from the form data
        username = self.features.getvalue('username')  # This assumes 'username' is the name of the input field
        return username


    def handle_update_profile(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)

        # Extract user data from the form
        username = data.get('inputUsername', [None])[0]
        c_username = data.get('inputCurrentUsername',[None])[0]
        first_name = data.get('inputFirstName', [None])[0]
        last_name = data.get('inputLastName', [None])[0]
        email = data.get('inputEmail', [None])[0]
        current_password = data.get('inputCurrentPassword', [None])[0]
        new_password = data.get('inputNewPassword', [None])[0]
        print(username)
        print(current_password)
        
        if self.validate_(c_username, current_password):
            self.update_user_profile(c_username, first_name, last_name, email, new_password)
            self.send_response(200)  # OK
            self.end_headers()
            self.wfile.write(b'{"message": "Profile updated successfully"}')
        else:
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'{"error": "Current password is incorrect"}')


    def get_user_info(self, username):
        connection = sqlite3.connect('users.db')  # Update this path to your database
        cursor = connection.cursor()
        
        # Query to fetch user information based on the username
        cursor.execute("SELECT first_name, last_name, email, role FROM users WHERE username=?", (username,))
        user_info = cursor.fetchone()
        
        connection.close()
    
        return user_info        

    # Validate the user's current password
    def validate_(self, c_username, current_password):
        connection = sqlite3.connect('users.db')  # Path to your database
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (c_username, current_password))
        user = cursor.fetchone()
        
        connection.close()
        
        return user is not None

    # Update the user's profile in the database
    def update_user_profile(self, c_username, first_name, last_name, email, new_password):
        connection = sqlite3.connect('users.db')  # Path to your database
        cursor = connection.cursor()

        # Update the user information including the username
        cursor.execute("""
            UPDATE users
            SET first_name = ?, last_name = ?, email = ?, password = ?
            WHERE username = ?
        """, (first_name, last_name, email, new_password, c_username))

        connection.commit()
        connection.close()

    def validate_user(self, username, password):
        connection = sqlite3.connect('users.db')  # Update this path to your database
        cursor = connection.cursor()
        
        # Query to check if the user exists
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        print(user)
        # Close the database connection
        connection.close()
        
        if user:
            print(user)
            return user[0]  # Return the role of the user
        else:
            return None  # Return None if user not found

    def insert_data(self, features, predicted_severity, uploaded_by):
        conn = sqlite3.connect(DB_NAME_)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accident_data (
                Age_band_of_driver, Driving_experience, Road_surface_type, Road_surface_conditions, Light_conditions, 
                Weather_conditions, Area_accident_occured, Lanes_or_Medians, Types_of_Junction, 
                Number_of_vehicles_involved, Vehicle_movement, Cause_of_accident, predicted_severity, date, uploaded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            features['Age_band_of_driver'], features['Driving_experience'], features['Road_surface_type'], 
            features['Road_surface_conditions'], features['Light_conditions'], features['Weather_conditions'], 
            features['Area_accident_occured'], features['Lanes_or_Medians'], features['Types_of_Junction'], 
            features['Number_of_vehicles_involved'], features['Vehicle_movement'], features['Cause_of_accident'], 
            predicted_severity, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), uploaded_by
        ))
        conn.commit()
        conn.close()

    def send_email(self, recipient, subject, body):
            print("reaching....")
            # Replace with your actual SMTP configuration
            smtp_username = 'mediconnectotp@gmail.com'
            smtp_password = 'fdio bdqo nhwt pous'
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587

            # Create the message
            message = MIMEMultipart()
            message['From'] = smtp_username
            message['To'] = recipient
            message['Subject'] = subject

            message.attach(MIMEText(body, 'plain'))

            try:
                # Send email
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(smtp_username, recipient, message.as_string())
                    print(f'Email sent to {recipient}')
            except Exception as e:
                print(f'Error sending email to {recipient}: {e}')

    def insert_user(self, first_name, last_name, email, role, username, password):
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO users (first_name, last_name, email, role, username, password)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (first_name, last_name, email, role, username, password))
                    conn.commit()
                    conn.close()




def run(server_class=http.server.HTTPServer, handler_class=SimpleHTTPRequestHandler):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    server_address = ('0.0.0.0', PORT)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {PORT}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
