import cv2
import pytesseract
import re
import logging
from collections import Counter
from ultralytics import YOLO



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_video(video_path, output_video_path='annotated_video.mp4', model_path='epoch5.pt', confidence_threshold=0.5):
   
    extracted_texts = set()  

    # Load the YOLO model
    model = YOLO(model_path)

    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Couldn't open video file.")
        return None, None

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    frame_number = 1
    max_license_plates = 0 
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        resized_frame = cv2.resize(frame, (640, 640))  

        
        results = model.predict(resized_frame)
        class_count = {}


        # If results are detected
        if results and len(results[0].boxes) > 0:
           
            
            detected_objects = results[0].boxes
            for obj in detected_objects:
                class_id = int(obj.cls.item())
                class_label = model.names[class_id]
                if class_label in class_count:
                    class_count[class_label] += 1
                else:
                    class_count[class_label] = 1
              
                bbox = obj.xywh[0].tolist()
                confidence = obj.conf[0]  
                # Check if the confidence score is above the threshold
                if confidence >= confidence_threshold:
                    x_center, y_center, width, height = map(int, bbox)
                    x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
                    x2, y2 = int(x_center + width / 2), int(y_center + height / 2)
                    cropped_img = resized_frame[y1:y2, x1:x2]
                    

                    # Apply OCR to the cropped image
                    extracted_text = pytesseract.image_to_string(cropped_img, config='--psm 6')

                    # Ensure the text has exactly 6 characters
                    clean_text = re.sub(r'\W+', '', extracted_text)  # Remove non-alphanumeric characters
                    if len(clean_text) == 6:
                        extracted_texts.add(clean_text.strip())

                    # Annotate the frame with bounding boxes and detected text
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, extracted_text.strip(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


            print(f"Frame {frame_number}:")
            for label, count in class_count.items():
                print(f"Number of {label}: {count}")
                if label == "License_Plate":  
                    max_license_plates = max(max_license_plates, count) 
        else:
       
            print(f"Frame {frame_number}:\n No Lisence plate is detected.")
            
        out.write(frame)
        frame_number += 1
    print(f"Total number of Lisence plate detected: {max_license_plates}")
    # Release resources
    cap.release()
    out.release()

    # Check if any text was extracted
    if extracted_texts:
        print(extracted_texts)
        
        return ', '.join(extracted_texts), output_video_path
    else:
        return "Sorry, no lisence plate number is extracted because of the video qaulity.", output_video_path

