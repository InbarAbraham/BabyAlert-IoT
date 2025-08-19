import os
import sys
import time
import cv2
import numpy as np
import requests
from ultralytics import YOLO
import RPi.GPIO as GPIO

'''
This code, running on your Raspberry Pi,
turns on a red light to indicate that the car is unlocked.
When you press the button, the car is locked. 
Then, the camera turns on, and if a baby is detected, it sends a Telegram alert.
'''

def send_telegram_alert(message: str):
    """
    Sends a message via Telegram bot to the configured chat ID.
    """
    bot_token = 'your_bot_token'
    chat_id = 'your_chat_id'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    payload = {
        'chat_id': chat_id,
        'text': message
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
        else:
            print("Telegram alert sent!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        
        
# === CONFIGURATION SECTION ===
model_path = "/home/pi/model/my_model_ncnn_model"
img_source = "usb0"  # USB camera device
min_thresh = 0.5 # Minimum confidence threshold for detection
user_res = "640x480" # Resolution for the camera
record = False # Whether to record video to file

# === Load MODEL ===
if not os.path.exists(model_path):
    print("? ERROR: YOLO model not found.")
    sys.exit()

model = YOLO(model_path, task='detect')
labels = model.names # Class labels used by the model

# === GPIO SETUP ===
lamp_pin = 17 # GPIO pin controlling the lamp
button_pin = 27 # GPIO pin connected to the "lock" button

GPIO.setmode(GPIO.BCM)
GPIO.setup(lamp_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Turn the lamp ON to indicate "car is unlocked"
GPIO.output(lamp_pin, GPIO.HIGH) 
print("Lamp is ON - The car is unlocked. Waiting for lock to start camera...")

# Wait until the button is pressed for locking the car
while GPIO.input(button_pin) == GPIO.HIGH:
    time.sleep(0.1)

# Car locked, turn lamp OFF and start detection
GPIO.output(lamp_pin, GPIO.LOW)
print("Button pressed turning OFF lamp and starting detection.")

# === CAMERA SETUP ===
usb_idx = 0
if img_source.startswith("usb"):
    usb_idx = int(img_source[3:])
    source_type = 'usb'
else:
    print("Invalid source.")
    sys.exit()

# === Resolution ===
resize = False
if user_res:
    try:
        resW, resH = map(int, user_res.lower().split('x'))
        resize = True
    except:
        print("Invalid resolution format. Use 'WIDTHxHEIGHT'.")
        sys.exit()

# Open the USB camera
cap = cv2.VideoCapture(usb_idx)
if resize:
    cap.set(3, resW)
    cap.set(4, resH)
if not cap.isOpened():
    print("Failed to open USB camera.")
    sys.exit()

# === Colors for bounding boxes ===
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106)]

# === Frame Loop ===
fps_log = []
alert_sent = False  # Ensure alert is sent only once per run

# === MAIN DETECTION LOOP ===
while True:
    t_start = time.time()
    ret, frame = cap.read() # Capture a single frame from the USB camera
    if not ret:
        print("Done with video/camera.")
        break

    if resize:
        frame = cv2.resize(frame, (resW, resH))

    # Run the YOLO model on the frame (no console output due to verbose=False)
    results = model(frame, verbose=False)
    detections = results[0].boxes
    detected = [] # Initialize list to store class names detected in this frame
    
    for box in detections:
        conf = box.conf.item() # Extract confidence score of the detection

        # Skip detections below the minimum confidence threshold
        if conf < min_thresh:
            continue
        
         # Get bounding box coordinates (x1, y1, x2, y2)
        xyxy = box.xyxy.cpu().numpy().squeeze().astype(int)
        xmin, ymin, xmax, ymax = xyxy
        class_id = int(box.cls.item())
        class_name = labels[class_id]
        color = bbox_colors[class_id % len(bbox_colors)]

        # === Drawing the Detection on the Frame ===
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        label = f"{class_name}: {int(conf*100)}%" # Format label with class name and confidence (e.g., "Kid: 97%")
        
        # Get label size to position it correctly above the box
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_ymin = max(ymin, label_size[1] + 10)
        
        # Draw filled rectangle behind the label text
        cv2.rectangle(frame, (xmin, label_ymin - label_size[1] - 10),
                      (xmin + label_size[0], label_ymin + 5), color, cv2.FILLED)
        
        # Draw the label text
        cv2.putText(frame, label, (xmin, label_ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

        detected.append(class_name)
        
        # Alert logic: when 'Kid' is detected
        if class_name == 'Kid' and not alert_sent:
            send_telegram_alert("ALERT: A kid was detected inside the locked car!")
            alert_sent = True

    # Calculate and show FPS
    fps = 1.0 / (time.time() - t_start)
    fps_log.append(fps)
    if len(fps_log) > 100:
        fps_log.pop(0)

    cv2.putText(frame, f"FPS: {np.mean(fps_log):.2f}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Show video title
    cv2.imshow("Baby Alert", frame)

    # Press 'q' to quit
    key = cv2.waitKey(5)
    if key == ord('q'):
        break

# === CLEANUP SECTION ===
print(f"Avg FPS: {np.mean(fps_log):.2f}")
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()

# Display all unique labels detected
unique_detected = set(detected)
print(unique_detected)