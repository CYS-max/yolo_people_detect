# utils/excel_export.py
import xlsxwriter

def export_attendance_excel(save_file, data_list, class_name):
    workbook = xlsxwriter.Workbook(save_file)
    worksheet = workbook.add_worksheet("考勤结果")
    headers = ["文件名","到场人数","班级总人数","缺勤人数","出勤率%","图片路径"]
    for col,h in enumerate(headers):
        worksheet.write(0,col,h)
    from utils.class_tool import calc_absent_rate
    for row,item in enumerate(data_list,start=1):
        stat = calc_absent_rate(class_name,item["person_count"])
        worksheet.write(row,0,item["filename"])
        worksheet.write(row,1,item["person_count"])
        worksheet.write(row,2,stat["total"])
        worksheet.write(row,3,stat["absent"])
        worksheet.write(row,4,stat["attendance_rate"])
        worksheet.write(row,5,item["full_path"])
    workbook.close()
