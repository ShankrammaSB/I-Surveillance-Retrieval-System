import cv2
import datetime
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog

# ========================
# SELECT MODE
# ========================
print("1. Use Webcam")
print("2. Use Video File")
choice = input("Enter choice: ")

if choice == "1":
    cap = cv2.VideoCapture(0)
else:
    root = tk.Tk()
    root.withdraw()
    video_path = filedialog.askopenfilename(title="Select Video File")

    if not video_path:
        print("No video selected")
        exit()

    cap = cv2.VideoCapture(video_path)

# ========================
# LOAD MODEL
# ========================
model = YOLO("yolov8n.pt")

log_file = open("events.txt", "w")

previous_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    person_count = 0
    bag_detected = False
    suspicious = False

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])

            if conf < 0.6:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Person
            if label == "person":
                person_count += 1
                color = (0, 255, 0)

            # Bag detection
            elif label in ["backpack", "handbag"]:
                bag_detected = True
                color = (255, 0, 0)

            # Vehicles
            elif label in ["car", "truck", "bus"]:
                color = (0, 255, 255)

            else:
                color = (200, 200, 200)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # ========================
    # SMART RULES
    # ========================

    # Crowd
    if person_count >= 4:
        suspicious = True

    # Sudden spike
    if previous_count != 0 and (person_count - previous_count) >= 2:
        suspicious = True

    # Abandoned bag
    if bag_detected and person_count == 0:
        suspicious = True

    # Normal override
    if person_count <= 1 and not bag_detected:
        suspicious = False

    previous_count = person_count

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if suspicious:
        status = "🚨 Suspicious Activity"
        color = (0, 0, 255)
    else:
        status = "✅ Normal Activity"
        color = (0, 255, 0)

    # ========================
    # LOG ONLY IMPORTANT EVENTS
    # ========================
    if suspicious:
        event = f"{status} at {timestamp} | people={person_count}, bag={bag_detected}"
        print(event)
        log_file.write(event + "\n")

    # ALERT
    if suspicious:
        print("🚨 ALERT TRIGGERED!")

    cv2.putText(frame, status, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("AI Surveillance System", frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

log_file.close()
cap.release()
cv2.destroyAllWindows()