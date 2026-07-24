# streamlit_web.py（仅修改单图、视频模块，其余不变）
import streamlit as st
import pandas as pd
from core.detect_engine import single_image_detect,batch_folder_detect,video_detect
from utils.class_tool import load_class_info,calc_absent_rate
from utils.excel_export import export_attendance_excel
import tempfile,os

st.title("智眸慧眼—基于YOLO26人数统计系统")
class_list = list(load_class_info().keys())
choose_class = st.selectbox("选择班级",class_list)
mode = st.radio("识别模式",["单张图片","文件夹批量压缩上传","视频检测"])

if mode=="单张图片":
    img = st.file_uploader("上传图片",type=["jpg","png","jpeg"])
    if img:
        tmp = tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(img.name)[1])
        tmp.write(img.read())
        tmp.close()
        cnt, annotated_img, _ = single_image_detect(tmp.name)
        st.image(annotated_img, caption="带框标注结果")  # 直接显示带框图
        stat = calc_absent_rate(choose_class,cnt)
        st.write(f"到场：{cnt}，总人数{stat['total']}，缺勤{stat['absent']}，出勤率{stat['attendance_rate']}%")
        os.unlink(tmp.name)

elif mode=="文件夹批量压缩上传":
    st.info("把整个文件夹压缩为zip上传")
    zip_file = st.file_uploader("上传zip",type="zip")
    if zip_file:
        import zipfile
        with tempfile.TemporaryDirectory() as dir_tmp:
            zip_path = os.path.join(dir_tmp,"a.zip")
            open(zip_path,"wb").write(zip_file.read())
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(dir_tmp)
            res = batch_folder_detect(dir_tmp)
            df = pd.DataFrame(res)
            stats = [calc_absent_rate(choose_class,x["person_count"]) for x in res]
            df["班级总人数"]=[s["total"] for s in stats]
            df["缺勤人数"]=[s["absent"] for s in stats]
            df["出勤率%"]=[s["attendance_rate"] for s in stats]
            st.dataframe(df)
            save_path = tempfile.NamedTemporaryFile(delete=False,suffix=".xlsx")
            save_path.close()
            export_attendance_excel(save_path.name,res,choose_class)
            st.download_button("下载Excel报表",open(save_path.name,"rb"),"attendance.xlsx")

elif mode=="视频检测":
    vid = st.file_uploader("上传视频",type=["mp4","avi"])
    interval = st.slider("抽帧间隔",10,60,30)
    if vid:
        tmp = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
        tmp.write(vid.read())
        tmp.close()
        frame_counts, avg, total_unique = video_detect(tmp.name,frame_interval=interval)
        stat = calc_absent_rate(choose_class,avg)
        st.write(f"每帧到场人数：{frame_counts}")
        st.write(f"平均到场：{avg}，视频总出现人数（去重）：{total_unique}")
        st.write(f"平均缺勤：{stat['absent']}，平均出勤率：{stat['attendance_rate']}%")
        df_plot = pd.DataFrame({"帧序号":range(len(frame_counts)),"到场人数":frame_counts})
        st.line_chart(df_plot,x="帧序号",y="到场人数")
        os.unlink(tmp.name)
