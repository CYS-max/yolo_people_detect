# utils/class_tool.py
import json
from core import config

def load_class_info():
    with open(config.CLASS_JSON_PATH,"r",encoding="utf-8") as f:
        return json.load(f)

def get_class_total(class_name):
    data = load_class_info()
    return data.get(class_name,0)

def calc_absent_rate(class_name, present_num):
    total = get_class_total(class_name)
    if total==0:
        return {"total":0,"absent":0,"rate":0}
    absent = total - present_num
    rate = round(present_num/total*100,2)
    return {
        "total":total,
        "absent":absent,
        "attendance_rate":rate
    }
