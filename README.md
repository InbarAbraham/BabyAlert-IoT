# 👶 Baby Alert Detection System

A Raspberry Pi–powered real-time monitoring system that detects the presence of a baby in a locked car using an AI-powered camera model. If a baby is detected, the system sends an instant alert via Telegram.

---

## 🧠 Project Overview

- **Goal**: Prevent life-threatening scenarios by alerting parents if a baby is detected in a locked car.
- **Technology**: Raspberry Pi, USB camera, YOLOv11 model, Telegram Bot integration.
- **Detection Flow**:
  1. Lamp ON = car is unlocked.
  2. Once the lock button is pressed, the system activates the camera and model.
  3. If a baby is detected, a Telegram alert is sent to the parent.

---

## 🛠 Hardware Components

- 🧠 **Raspberry Pi** – central controller.
- 📷 **USB Camera** – for capturing real-time video.
- 💡 **LED Lamp** – indicates whether the car is locked or unlocked.
- 🔘 **Button** – simulates the car locking mechanism.

---

## 💻 Software Stack

- **Python** – programming language used throughout the project.
- **OpenCV** – handles video streaming and frame processing.
- **PyTorch + YOLOv11 (Ultralytics)** – for object detection.
- **RPi.GPIO** – controls the Raspberry Pi GPIO pins.
- **Label Studio** – used for annotating training images.
- **Telegram Bot API** – used to send alerts when a baby is detected.

---

## 🧪 Custom Model Training Process

###  Collect and Label Data & Train the Detection Model
- We collected 500 images of babies from various sources.
- Training is handled via [`Train_YOLO_Models.ipynb`](Train_YOLO_Models.ipynb).
- YOLOv11 from Ultralytics was trained on our custom dataset.
- The trained model is exported and moved to the Raspberry Pi for deployment.

---

## 📲 Telegram Bot Integration
- Telegram bot created with **BotFather**.  
- Alerts sent via **Telegram Bot API** using Python.  
