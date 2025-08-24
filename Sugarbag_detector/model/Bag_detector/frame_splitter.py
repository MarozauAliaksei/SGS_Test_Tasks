import cv2
import os

def extract_frames(video_path, output_dir, step=10):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    saved = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_id % step == 0:
            filename = os.path.join(output_dir, f"frame_{saved}.jpg")
            cv2.imwrite(filename, frame)
            saved += 1
        frame_id += 1
    cap.release()

extract_frames("task.mp4", "dataset/raw_images", step=10)
