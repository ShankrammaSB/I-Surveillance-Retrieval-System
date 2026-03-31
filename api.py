from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import os
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

model = YOLO("yolov8n.pt")

VIDEO_PATH = "uploaded_video.mp4"

cap = None
video_ready = False   # 🔥 IMPORTANT
max_people = 0


def process_frame(frame):
    global max_people

    person_count = 0

    try:
        results = model(frame)

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                label = model.names[cls]

                if label == "person":
                    person_count += 1

                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0,255,0), 2)

                cv2.putText(frame, label,
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0,255,0), 2)

    except Exception as e:
        print("YOLO ERROR:", e)

    if person_count > max_people:
        max_people = person_count

    cv2.putText(frame, f"People: {person_count}", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    cv2.putText(frame, f"Max: {max_people}", (20,80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    return frame


@app.route("/frame")
def frame():
    global cap, video_ready

    try:
        # 🔴 No video yet
        if not video_ready:
            blank = np.ones((480,640,3), dtype=np.uint8)*255
            cv2.putText(blank, "UPLOAD VIDEO", (150,240),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
            _, buffer = cv2.imencode('.jpg', blank)
            return Response(buffer.tobytes(), mimetype='image/jpeg')

        # 🔥 Safe cap usage
        if cap is None:
            cap = cv2.VideoCapture(VIDEO_PATH)

        if not cap.isOpened():
            print("Video open failed")
            return Response(status=500)

        success, frame = cap.read()

        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = cap.read()

        frame = process_frame(frame)

        _, buffer = cv2.imencode('.jpg', frame)
        return Response(buffer.tobytes(), mimetype='image/jpeg')

    except Exception as e:
        print("FRAME ERROR:", e)
        return Response(status=500)


@app.route("/upload", methods=["POST"])
def upload():
    global cap, video_ready, max_people

    try:
        file = request.files["file"]
        file.save(VIDEO_PATH)

        # 🔥 CRITICAL FIX
        if cap is not None:
            cap.release()

        cap = None
        video_ready = True
        max_people = 0

        print("Video uploaded successfully")

        return {"message": "uploaded"}

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return {"error": "upload failed"}, 500


@app.route("/summary")
def summary():
    return jsonify({
        "max_people": max_people
    })


if __name__ == "__main__":
    app.run(port=5000)