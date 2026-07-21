import streamlit as st
from PIL import Image
from ultralytics import YOLO
import os

# -------------------------- 【你的原版逻辑 完全未修改】 --------------------------
# 加载训练好的最优检测模型
model = YOLO("best.pt")

# YOLO检测统计函数，100%复用你Qt里的判断逻辑，无任何改动
def detect_count_person(file_path):
    # YOLO模型检测、统计人数
    detect_res = model(file_path, save=True, conf=0.35, iou=0.65)
    save_location = detect_res[0].save_dir

    people_num = 0
    min_w = 25
    min_h = 35
    max_aspect = 3.0  # 宽高比上限：高/宽>3判定为细长书包，直接排除
    boxes = detect_res[0].boxes
    for box in boxes:
        if box.cls.item() != 0:
            continue
        x1, y1, x2, y2 = box.xyxy[0]
        box_w = x2 - x1
        box_h = y2 - y1
        if box_w >= min_w and box_h >= min_h:
            aspect = box_h / box_w
            if aspect < max_aspect:
                people_num += 1
    return people_num, save_location, detect_res[0].plot()
# -----------------------------------------------------------------------------

# ========== Streamlit网页界面（替代原来的PyQt窗口） ==========
st.set_page_config(page_title="智眸慧眼——课堂实时考勤人数统计系统", layout="wide")
st.title("智眸慧眼——课堂实时考勤人数统计系统")

# 上传图片（替代QFileDialog）
upload_img = st.file_uploader("上传课堂照片", type=["jpg", "png", "jpeg"])

if upload_img is not None:
    # 1. 展示原图（替代QLabel原图显示）
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("原始图片")
        img_ori = Image.open(upload_img)
        st.image(img_ori, use_column_width=True)

    # 保存临时本地路径给YOLO读取
    temp_path = "temp_upload.jpg"
    img_ori.save(temp_path)

    # 2. 调用你原版检测计数逻辑
    total_people, save_path, result_img = detect_count_person(temp_path)

    # 3. 展示带框检测图
    with col2:
        st.subheader("检测标注结果")
        st.image(result_img, use_column_width=True)

    # 4. 输出识别文本（替代QTextEdit）
    output_text = f"""=======识别完成=======
图片路径：{upload_img.name}
课堂到场总人数：{total_people}
带检测框标注图片云端保存目录：{save_path}"""
    st.text_area("识别结果", value=output_text, height=150)

# 缓存模型，云端重复打开不重复下载加载
@st.cache_resource
def load_model():
    return YOLO("best.pt")