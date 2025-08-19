# 👶 Baby Alert Detection System

A Raspberry Pi–powered real-time monitoring system that detects the presence of a baby in a locked car using a camera and a custom-trained AI model. If a baby is detected, the system sends an instant alert via Telegram.

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

### 1. 📸 Collect and Label Data
- We collected **500 images** of babies from various sources.
- Using **Label Studio**, we manually tagged each image with bounding boxes around the baby.

### 2. 🧠 Train the Detection Model
- Training is handled via [`Train_YOLO_Models.ipynb`](Train_YOLO_Models.ipynb).
- YOLOv11 from Ultralytics was trained on our custom dataset.
- The trained model is exported and moved to the Raspberry Pi for deployment.

---

## 📲 Telegram Bot Integration

### Step-by-step:

1. Open Telegram and search for @BotFather:
- Start a conversation with BotFather and send the /newbot command. 
- Follow BotFather's prompts to name your bot and choose a username (which must end with "bot"). 
- BotFather will provide you with a bot token, which is your access key and needs to be kept safe. 

2. Connect Your Bot to a Backend Server:
- You'll need to use a programming language like Python, Java, or Golang to create your bot's logic and connect it to the Telegram Bot API. 
- Choose a Programming Language and Library: Python is a popular choice, using libraries like pyTelegramBotAPI. 
- Set Up Your Project: Create a new project directory, install the necessary libraries, and initialize the bot. 
- Implement Bot Logic: Write code to handle messages, commands, and other bot interactions. 
- Test and Deploy: Test your bot locally and then deploy it to a server. 

**Follow for full and detailed instructions over here: https://core.telegram.org/bots/api**

 ## ⚙️ Install Dependencies:
- Install The requirements.txt file by the command: `pip install -r requirements.txt`