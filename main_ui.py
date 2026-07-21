import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QTextEdit
from PyQt5.QtGui import QPixmap
from ultralytics import YOLO

# 加载训练好的最优检测模型
model = YOLO("runs/detect/train_output/person_model-6/weights/best.pt")

# 软件主窗口类
class SystemWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 窗口基础设置
        self.setWindowTitle("智眸慧眼——课堂实时考勤人数统计系统")
        self.setFixedSize(900, 700)

        # 1.上传图片按钮
        self.upload_btn = QPushButton("上传课堂照片", self)
        self.upload_btn.setGeometry(50, 20, 180, 40)
        self.upload_btn.clicked.connect(self.select_image)

        # 2.图片展示区域
        self.image_display = QLabel(self)
        self.image_display.setGeometry(50, 80, 800, 450)

        # 3.识别结果文本框（显示人数）
        self.result_box = QTextEdit(self)
        self.result_box.setGeometry(50, 550, 800, 100)
        self.result_box.setReadOnly(True)

    # 上传图片触发函数
    def select_image(self):
        # 弹出文件选择框，只允许选择图片
        file_path, file_type = QFileDialog.getOpenFileName(
            self, "选择课堂图片", "", "图片文件 (*.jpg *.png *.jpeg)"
        )
        # 未选择图片直接返回
        if not file_path:
            return

        # 在界面展示原图
        original_pic = QPixmap(file_path)
        self.image_display.setPixmap(original_pic.scaled(self.image_display.size()))

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
        save_location = detect_res[0].save_dir

        # 输出识别信息到文本框
        output_text = f"""=======识别完成=======
图片路径：{file_path}
课堂到场总人数：{people_num}
带检测框标注图片保存位置：{save_location}"""
        self.result_box.setText(output_text)

# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemWindow()
    window.show()
    sys.exit(app.exec_())