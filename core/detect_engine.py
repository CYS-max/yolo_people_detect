from ultralytics import YOLO
import cv2
import os
from core import config

model = YOLO("best.pt")

def single_image_detect(img_path, conf=config.DEFAULT_CONF, iou=config.DEFAULT_IOU):
    """单图检测+返回带框标注图"""
    results = model.predict(img_path, conf=conf, iou=iou, save=True, project=config.SAVE_DETECT_DIR)
    count = 0
    annotated_img = results[0].plot()
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        w = x2 - x1
        h = y2 - y1
        if w < config.MIN_W or h < config.MIN_H:
            continue
        aspect = max(w, h) / min(w, h)
        if aspect > config.MAX_ASPECT:
            continue
        count += 1
    save_path = results[0].save_dir
    return count, annotated_img, save_path

def batch_folder_detect(folder_path, conf=config.DEFAULT_CONF, iou=config.DEFAULT_IOU):
    support_suffix = [".jpg", ".png", ".jpeg", ".JPG", ".PNG"]
    res_list = []
    for filename in os.listdir(folder_path):
        ext = os.path.splitext(filename)[1]
        if ext not in support_suffix:
            continue
        full_path = os.path.join(folder_path, filename)
        person_count, _, save_path = single_image_detect(full_path, conf, iou)
        res_list.append({
            "filename": filename,
            "full_path": full_path,
            "person_count": person_count,
            "save_path": str(save_path)
        })
    return res_list

def video_detect(video_path, frame_interval=6, conf=0.28, iou=0.55):
    frame_idx = 0
    frame_counts = []
    track_appear_times = dict()
    MIN_TRACK_FRAME = 5  # 从4上调至5，短命分裂ID更容易被剔除

    results_gen = model.track(
        video_path,
        conf=conf,
        iou=iou,
        persist=True,
        tracker="botsort.yaml",
        stream=True
    )
    for result in results_gen:
        frame_idx += 1
        if frame_idx % frame_interval != 0:
            continue
        cnt = 0
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            w = x2 - x1
            h = y2 - y1
            if w < config.MIN_W or h < config.MIN_H:
                continue
            aspect = max(w, h) / min(w, h)
            if aspect > config.MAX_ASPECT:
                continue
            cnt += 1
            if box.id is not None:
                tid = int(box.id)
                track_appear_times[tid] = track_appear_times.get(tid, 0) + 1
        frame_counts.append(cnt)

    avg = round(sum(frame_counts)/len(frame_counts),2) if frame_counts else 0
    valid_ids = [tid for tid, times in track_appear_times.items() if times >= MIN_TRACK_FRAME]
    total_unique = len(valid_ids)
    return frame_counts, avg, total_unique
