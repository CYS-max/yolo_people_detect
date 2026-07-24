# core/config.py
DEFAULT_CONF = 0.35
DEFAULT_IOU = 0.65
MIN_W = 12
MIN_H = 15
MAX_ASPECT = 4.5
SAVE_DETECT_DIR = "./runs/detect"
SAVE_VIDEO_FRAME_DIR = "./runs/video_frame"
CLASS_JSON_PATH = "class_info.json"
import os
os.makedirs(SAVE_DETECT_DIR, exist_ok=True)
os.makedirs(SAVE_VIDEO_FRAME_DIR, exist_ok=True)
