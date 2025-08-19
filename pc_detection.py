import os
import sys
import glob
import time
import cv2
import numpy as np
import math
import requests
from ultralytics import YOLO

'''
This code running on your local PC:
This code opens your USB camera and sends a Telegram alert if a baby is detected.
'''

# === SETUP YOUR CONFIG HERE ===
model_path = "my_model.pt"
img_source = "usb0"  # Can be: "usb0", a path to image, folder, or video
min_thresh = 0.5
user_res = "640x480"
record = False

# === Load model ===
if not os.path.exists(model_path):
    print("❌ ERROR: YOLO model not found.")
    sys.exit()

model = YOLO(model_path, task='detect')
labels = model.names

# === Source detection ===
img_ext_list = ['.jpg', '.jpeg', '.png', '.bmp']
vid_ext_list = ['.avi', '.mp4', '.mov', '.mkv']

source_type = ''
usb_idx = 0

if os.path.isdir(img_source):
    source_type = 'folder'
elif os.path.isfile(img_source):
    ext = os.path.splitext(img_source)[1]
    source_type = 'image' if ext.lower() in img_ext_list else 'video' if ext.lower() in vid_ext_list else ''
elif img_source.startswith("usb"):
    source_type = 'usb'
    usb_idx = int(img_source[3:])
else:
    print("❌ Invalid source.")
    sys.exit()

# === Resolution ===
resize = False
if user_res:
    try:
        resW, resH = map(int, user_res.lower().split('x'))
        resize = True
    except:
        print("❌ Invalid resolution format. Use 'WIDTHxHEIGHT'.")
        sys.exit()

# === Video/Camera Setup ===
if source_type in ['video', 'usb']:
    cap = cv2.VideoCapture(usb_idx if source_type == 'usb' else img_source, cv2.CAP_DSHOW)
    if resize:
        cap.set(3, resW)
        cap.set(4, resH)
    if not cap.isOpened():
        print("❌ Failed to open video/camera source.")
        sys.exit()

if record:
    if source_type not in ['video', 'usb']:
        print("❌ Recording only supported for video/camera.")
        sys.exit()
    if not resize:
        print("❌ Please set resolution to enable recording.")
        sys.exit()
    recorder = cv2.VideoWriter('demo1.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (resW, resH))

# === Colors for bounding boxes ===
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133),
               (88,159,106), (96,202,231), (159,124,168), (169,162,241)]

# === Frame loop ===
imgs_list = []
if source_type == 'folder':
    imgs_list = [f for f in glob.glob(img_source + '/*') if os.path.splitext(f)[1].lower() in img_ext_list]
elif source_type == 'image':
    imgs_list = [img_source]

img_count = 0
fps_log = []

while True:
    t_start = time.time()

    if source_type in ['image', 'folder']:
        if img_count >= len(imgs_list):
            print("✅ Done with all images.")
            break
        frame = cv2.imread(imgs_list[img_count])
        img_count += 1
    elif source_type in ['video', 'usb']:
        ret, frame = cap.read()
        if not ret:
            print("✅ Done with video/camera.")
            break
    else:
        print("❌ Unsupported source type.")
        break

    if resize:
        frame = cv2.resize(frame, (resW, resH))

    results = model(frame, verbose=False)
    detections = results[0].boxes
    detected = []

    for box in detections:
        conf = box.conf.item()
        if conf < min_thresh:
            continue

        xyxy = box.xyxy.cpu().numpy().squeeze().astype(int)
        xmin, ymin, xmax, ymax = xyxy
        class_id = int(box.cls.item())
        class_name = labels[class_id]
        color = bbox_colors[class_id % len(bbox_colors)]

        # Draw bounding box and label
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        label = f"{class_name}: {int(conf*100)}%"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_ymin = max(ymin, label_size[1] + 10)
        cv2.rectangle(frame, (xmin, label_ymin - label_size[1] - 10),
                      (xmin + label_size[0], label_ymin + 5), color, cv2.FILLED)
        cv2.putText(frame, label, (xmin, label_ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

        detected.append(class_name)

    fps = 1.0 / (time.time() - t_start)
    fps_log.append(fps)
    if len(fps_log) > 100:
        fps_log.pop(0)

    if source_type in ['video', 'usb']:
        cv2.putText(frame, f"FPS: {np.mean(fps_log):.2f}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Baby Alert Detection", frame)
    if record:
        recorder.write(frame)

    key = cv2.waitKey(5 if source_type in ['video', 'usb'] else 0)
    if key == ord('q'):
        break
    elif key == ord('p'):
        cv2.imwrite('snapshot.png', frame)
    elif key == ord('s'):
        cv2.waitKey()

# === Cleanup ===
print(f"📊 Avg FPS: {np.mean(fps_log):.2f}")
if source_type in ['video', 'usb']:
    cap.release()
if record:
    recorder.release()
cv2.destroyAllWindows()

def send_telegram_alert(message: str):
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
            print(f"❌ Failed to send Telegram message: {response.text}")
        else:
            print("✅ Telegram alert sent!")
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")

unique_detected = set(detected)
print(unique_detected)

if 'Kid' in unique_detected:
    send_telegram_alert("🚨 ALERT: A kid was detected inside the locked car!")
    