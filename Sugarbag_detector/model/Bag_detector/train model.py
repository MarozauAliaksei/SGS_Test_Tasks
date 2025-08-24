from ultralytics import YOLO
import torch


def train_model():
    model = YOLO("yolo11n.pt")

    model.train(
        data="data.yaml",
        epochs=100,
        imgsz=640
    )


if __name__ == '__main__':
    torch.multiprocessing.freeze_support()
    train_model()