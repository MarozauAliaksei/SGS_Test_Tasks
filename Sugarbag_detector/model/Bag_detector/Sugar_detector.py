import cv2
from ultralytics import YOLO

# supervision

# АНИМАЦИЯ СЧЁТЧИКА
animations = []


def add_animation(x, y, delta):
    animations.append({
        "x": int(x),
        "y": int(y),
        "text": f"{'+' if delta > 0 else ''}{delta}",
        "color": (29, 110, 243) if delta > 0 else (241, 110, 29),
        "alpha": 1.0,
        "scale": 1.0,
        "direction": -2 if delta > 0 else 2  # вверх если +1, вниз если -1
    })


def draw_animations(frame):
    overlay = frame.copy()
    for anim in animations[:]:
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = anim["scale"]
        color = anim["color"]

        # Рисуем текст на временном кадре
        cv2.putText(
            overlay,
            anim["text"],
            (anim["x"], anim["y"]),
            font,
            scale,
            color,
            2,
            cv2.LINE_AA
        )

        cv2.addWeighted(overlay, anim["alpha"], frame, 1 - anim["alpha"], 0, frame)

        anim["y"] += anim["direction"]  # движение
        anim["alpha"] -= 0.03  # затухание
        anim["scale"] += 0.01  # легкое увеличение

        if anim["alpha"] <= 0:
            animations.remove(anim)
    return frame


def draw_label_with_icon(frame, x1, y1, label="Bag of sugar", icon=None):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2

    (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
    icon_h = text_h
    icon_w = text_h

    box_w = icon_w + 5 + text_w + 10
    box_h = max(icon_h, text_h) + 10

    x2 = x1 + box_w
    y2 = y1 - box_h - 5

    if y2 < 0:
        y2 = y1 + 5
    y1_tmp = y2

    x1, y1_tmp, x2, box_h = map(int, [x1, y1_tmp, x2, box_h])

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1_tmp), (x2, y1_tmp + box_h), (123, 120, 119), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

    if icon is not None:
        icon_resized = cv2.resize(icon, (icon_w, icon_h))
        roi = frame[y1_tmp + 5:y1_tmp + 5 + icon_h, x1 + 5:x1 + 5 + icon_w]
        if icon_resized.shape[2] == 4:
            icon_bgr = icon_resized[:, :, :3]
            mask = icon_resized[:, :, 3:] / 255.0
            roi[:] = (1 - mask) * roi + mask * icon_bgr
        else:
            roi[:] = icon_resized

    text_x = x1 + icon_w + 10
    text_y = y1_tmp + box_h - 7
    cv2.putText(frame, label, (int(text_x), int(text_y)), font, font_scale, (255, 255, 255), thickness)
    return frame


def process_video(input_path: str, output_path: str) -> bool:
    model = YOLO("runs/detect/train7/weights/best.pt")

    LINE_START = (210, 107)
    LINE_END = (404, 135)

    counter = 0
    track_history = {}
    cap = cv2.VideoCapture( input_path + "task.mp4")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter( output_path + 'output_video.mp4', fourcc, fps, (width, height))

    icon = cv2.imread("sugar.png", cv2.IMREAD_UNCHANGED)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True, classes=[0], show=False, conf=0.85, iou=0.84)

        cv2.line(frame, LINE_START, LINE_END, (29, 110, 243), 1, cv2.LINE_AA)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

                if track_id not in track_history:
                    track_history[track_id] = []

                track_history[track_id].append(center)
                if len(track_history[track_id]) > 30:
                    track_history[track_id].pop(0)

                if len(track_history[track_id]) >= 2:
                    prev_point = track_history[track_id][-2]
                    curr_point = track_history[track_id][-1]

                    def intersect(a, b, c, d):
                        def ccw(A, B, C):
                            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

                        return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)

                    if intersect(prev_point, curr_point, LINE_START, LINE_END):
                        direction = (curr_point[1] - prev_point[1])
                        if direction > 0:
                            counter -= 1
                            add_animation(center[0], center[1], -1)
                        else:
                            counter += 1
                            add_animation(center[0], center[1], +1)

                        print(f"Counter: {counter}")

                overlay = frame.copy()
                cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), (123, 120, 119), -1)
                alpha = 0.3
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (123, 120, 119), 2)
                frame = draw_label_with_icon(frame, x1, y1, "Bag of sugar", icon)

        # Рисуем основной счётчик
        overlay = frame.copy()
        cv2.rectangle(overlay, (frame.shape[1] - 180, frame.shape[0] - 60),
                      (frame.shape[1] - 20, frame.shape[0] - 20), (123, 120, 119), -1, cv2.LINE_AA)
        alpha = 0.5
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        cv2.putText(frame, f"Total: {counter}", (frame.shape[1] - 170, frame.shape[0] - 30),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

        # Рисуем анимации +1/-1
        frame = draw_animations(frame)

        out.write(frame)
        cv2.imshow("Conveyor", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
