import csv
import io
from flask import Flask, request, url_for, redirect, abort, make_response, jsonify
from markupsafe import escape

app = Flask(__name__)
app.json.ensure_ascii = False

# Dữ liệu mẫu (Câu 0.2)
STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

# --- PHẦN 0: HÀM PHỤ VÀ KHUNG TRANG ---

def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    st = STUDENTS[mssv]
    avg = average(st["scores"])
    return {
        "mssv": mssv,
        "name": st["name"],
        "lop": st["lop"],
        "scores": st["scores"],
        "average": avg,
        "rank": rank(avg)
    }

def layout(title, body):
    escaped_title = escape(title)
    home_url = url_for("index")
    students_url = url_for("student_list")
    search_url = url_for("search")
    
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{escaped_title} - Sổ điểm</title>
</head>
<body>
    <nav>
        <a href="{home_url}">Trang chủ</a> | 
        <a href="{students_url}">Sinh viên</a> | 
        <a href="{search_url}">Tìm kiếm sinh viên</a>
    </nav>
    <hr>
    <h1>{escaped_title}</h1>
    <div>{body}</div>
</body>
</html>"""

# --- PHẦN 1: GIAO DIỆN WEB (CÂU 1 - 6) ---

@app.route("/")
def index():
    total_students = len(STUDENTS)
    classes = len(set(st["lop"] for st in STUDENTS.values()))
    body = f"""<p>Tổng số sinh viên: {total_students}</p>
<p>Số lớp: {classes}</p>
<p><a href="{url_for('student_list')}">Danh sách sinh viên</a></p>
<p><a href="{url_for('api_student_list')}">API Sinh viên</a></p>"""
    return layout("Trang chủ", body)

@app.route("/students")
def student_list():
    lop_param = request.args.get("lop", "").strip()
    all_lops = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    
    nav_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for l in all_lops:
        nav_links.append(f'<a href="{url_for("student_list", lop=l)}">{escape(l)}</a>')
    filter_bar = " | ".join(nav_links)
    
    filtered = []
    for mssv in STUDENTS:
        summary = student_summary(mssv)
        if lop_param:
            if summary["lop"].lower() == lop_param.lower():
                filtered.append(summary)
        else:
            filtered.append(summary)
            
    if not filtered:
        table_html = "<p>Không có sinh viên phù hợp.</p>"
    else:
        rows = []
        for s in filtered:
            avg_str = str(s["average"]) if s["average"] is not None else "-"
            detail_url = url_for("student_detail", mssv=s["mssv"])
            rows.append(f"""<tr>
                <td><a href="{detail_url}">{escape(s['mssv'])}</a></td>
                <td>{escape(s['name'])}</td>
                <td>{escape(s['lop'])}</td>
                <td>{escape(avg_str)}</td>
                <td>{escape(s['rank'])}</td>
            </tr>""")
        table_html = f"""<table border="1">
            <tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr>
            {"".join(rows)}
        </table>"""
        
    body = f"<div>Thanh lọc: {filter_bar}</div><br>{table_html}"
    return layout("Danh sách sinh viên", body)

@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    
    s = student_summary(mssv)
    lop_url = url_for("student_list", lop=s["lop"])
    export_url = url_for("export_csv", mssv=mssv)
    short_url = url_for("student_short", mssv=mssv)
    
    scores_rows = "".join([
        f"<tr><td>{escape(str(hp))}</td><td>{escape(str(diem))}</td></tr>" 
        for hp, diem in s["scores"].items()
    ])
    scores_table = f'<table border="1"><tr><th>Học phần</th><th>Điểm</th></tr>{scores_rows}</table>' if scores_rows else "<p>Chưa có điểm học phần nào.</p>"
    
    body = f"""<p><b>Họ tên:</b> {escape(s['name'])}</p>
<p><b>MSSV:</b> {escape(s['mssv'])}</p>
<p><b>Lớp:</b> <a href="{lop_url}">{escape(s['lop'])}</a></p>
<p><b>Điểm TB:</b> {escape(str(s['average']) if s['average'] is not None else 'Chưa có')}</p>
<p><b>Xếp loại:</b> {escape(s['rank'])}</p>
<p><a href="{export_url}">Tải bảng điểm (CSV)</a> | Link rút gọn: <a href="{short_url}">{short_url}</a></p>
<h3>Bảng điểm chi tiết:</h3>
{scores_table}"""
    return layout(f"Chi tiết sinh viên {s['name']}", body)

@app.route("/sv/<mssv>")
def student_short(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)

@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    
    st = STUDENTS[mssv]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["hoc_phan", "diem"])
    for hp, diem in st["scores"].items():
        writer.writerow([hp, diem])
        
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response

@app.route("/search")
def search():
    q = request.args.get("q", "")
    q_clean = q.strip().lower()
    
    results = []
    if q_clean:
        for mssv, st in STUDENTS.items():
            if q_clean in mssv.lower() or q_clean in st["name"].lower():
                results.append(student_summary(mssv))
                
    form_html = f"""<form method="GET" action="{url_for('search')}">
    <input type="text" name="q" value="{escape(q)}" placeholder="Nhập từ khóa...">
    <button type="submit">Tìm kiếm</button>
</form>"""
    
    result_html = ""
    if q:
        result_html = f"<h3>Tìm thấy {len(results)} kết quả cho \"{escape(q)}\"</h3>"
        if results:
            items = "".join([
                f'<li><a href="{url_for("student_detail", mssv=s["mssv"])}">{escape(s["mssv"])} - {escape(s["name"])}</a> ({escape(s["lop"])})</li>' 
                for s in results
            ])
            result_html += f"<ul>{items}</ul>"
            
    return layout("Tìm kiếm sinh viên", form_html + result_html)

# --- PHẦN 2: API JSON (CÂU 7 - 8) ---

@app.route("/api/students", methods=["GET"])
def api_student_list():
    lop_param = request.args.get("lop")
    
    min_avg = None
    if "min_avg" in request.args:
        try:
            min_avg = float(request.args["min_avg"])
        except ValueError:
            abort(400, description="Tham số min_avg phải là số.")
            
    res = []
    for mssv in STUDENTS:
        summary = student_summary(mssv)
        if lop_param and summary["lop"].lower() != lop_param.lower():
            continue
        if min_avg is not None:
            if summary["average"] is None or summary["average"] < min_avg:
                continue
        res.append(summary)
    return jsonify(res)

@app.route("/api/students/<mssv>", methods=["GET"])
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên có MSSV = {mssv}.")
    return jsonify(student_summary(mssv))

@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE", "POST"])
def api_student_scores(mssv, course):
    if request.method == "POST":
        abort(405, description="Phương thức POST không được hỗ trợ trên endpoint này.")
        
    if mssv not in STUDENTS:
        abort(404, description=f"Không tìm thấy sinh viên có MSSV = {mssv}.")
        
    course_upper = course.upper()
    scores = STUDENTS[mssv]["scores"]
    
    if request.method == "GET":
        if course_upper not in scores:
            abort(404, description=f"Không tìm thấy điểm môn {course_upper}.")
        return jsonify({
            "mssv": mssv,
            "course": course_upper,
            "score": scores[course_upper]
        })
        
    if request.method == "DELETE":
        if course_upper not in scores:
            abort(404, description=f"Không tìm thấy điểm môn {course_upper}.")
        del scores[course_upper]
        return "", 204
        
    if request.method == "PUT":
        score_raw = request.args.get("score")
        if score_raw is None:
            abort(400, description="Thiếu tham số 'score'.")
        try:
            score_val = float(score_raw)
        except ValueError:
            abort(400, description="Tham số 'score' phải là số.")
            
        if not (0 <= score_val <= 10):
            abort(400, description="Điểm phải trong khoảng từ 0 đến 10.")
            
        is_new = course_upper not in scores
        scores[course_upper] = score_val
        
        summary = student_summary(mssv)
        res_payload = {
            "mssv": mssv,
            "course": course_upper,
            "score": score_val,
            "average": summary["average"]
        }
        
        if is_new:
            res = make_response(jsonify(res_payload), 201)
            res.headers["Location"] = url_for("api_student_scores", mssv=mssv, course=course_upper)
            return res
        else:
            return jsonify(res_payload), 200

# --- PHẦN 3: XỬ LÝ LỖI (CÂU 9) ---

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ"
    }
    code = getattr(error, "code", 500)
    title = titles.get(code, "Lỗi")
    description = getattr(error, "description", str(error))
    
    if request.path.startswith("/api/"):
        return jsonify({"error": title, "detail": description}), code
    else:
        body = f"<p><b>Mã lỗi:</b> {code}</p><p>{escape(description)}</p>"
        return layout(f"{code} - {title}", body), code
