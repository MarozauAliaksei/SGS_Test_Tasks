from ultralytics import YOLO
import cv2
import torch


def track_model():
    model = YOLO("runs/detect/train6/weights/best.pt")


    video_path = "task.mp4"
    cap = cv2.VideoCapture(video_path)

    results = model.track(
        source=video_path,
        show=True,
        save=True,
        conf=0.5,
        iou=0.5,
    )


if __name__ == '__main__':
    torch.multiprocessing.freeze_support()
    track_model()