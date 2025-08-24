import cv2


def extract_frame_by_number(video_path, frame_number, output_path):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Кадр {frame_number} сохранен как {output_path}")
    else:
        print(f"Ошибка: не удалось прочитать кадр {frame_number}")
    cap.release()



video_file = "task.mp4"
for _ in range(10):
    i = int(input())
    extract_frame_by_number(video_file, i, f"dataset/raw_images/{i}frame.jpg")