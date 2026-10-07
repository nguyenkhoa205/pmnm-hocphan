# BÀI TẬP TỔNG HỢP CHƯƠNG 3 - SỔ ĐIỂM LỚP HỌC

## 1. Kết quả `flask --app sodiem routes`
```text
Endpoint            Methods  Rule
------------------  -------  -----------------------------------------
api_student_detail  GET      /api/students/<mssv>
api_student_list    GET      /api/students
api_student_scores  DELETE, GET, POST, PUT /api/students/<mssv>/scores/<course>
export_csv          GET      /students/<mssv>/export
index               GET      /
search              GET      /search
static              GET      /static/<filename>
student_detail      GET      /students/<mssv>
student_list        GET      /students
student_short       GET      /sv/<mssv>