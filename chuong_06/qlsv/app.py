from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

# Khai báo header trả về văn bản thuần (tránh trình duyệt hiểu nhầm <Student ...> là thẻ HTML)
TEXT = {"Content-Type": "text/plain; charset=utf-8"}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- Khai báo Model Student ---
class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f'<Student {self.mssv} {self.name}>'

# --- Khởi tạo bảng ---
with app.app_context():
    db.create_all()

# --- Route Trang chủ ---
@app.get("/")
def home():
    students = db.session.scalars(db.select(Student)).all()
    return render_template("students.html", students=students)

# --- Route Thêm dữ liệu mẫu (Bước 5) ---
@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(db.select(func.count(Student.id)))
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa."

    an = Student(mssv="23T1020001", name="Nguyễn Văn An", gpa=8.5)
    db.session.add(an)
    db.session.add_all([
        Student(mssv="23T1020002", name="Trần Thị Bình", gpa=6.8),
        Student(mssv="23T1020003", name="Lê Hoàng Cường", gpa=9.1),
        Student(mssv="23T1020004", name="Phạm Minh Dũng", gpa=4.5),
        Student(mssv="23T1020005", name="Hoàng Thu Hà", gpa=7.4),
    ])
    db.session.commit()
    return "Đã thêm thành công 5 sinh viên mẫu!"

# ==========================================
# BƯỚC 6: ROUTE TRUY VẤN DỮ LIỆU
# ==========================================
@app.get("/thu-truy-van")
def try_queries():
    # Kiểm tra nếu chưa có dữ liệu thì thông báo ngay (tránh lỗi tính trung bình avg = None)
    if db.session.scalar(db.select(func.count(Student.id))) == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước.", TEXT

    lines = []
    
    # 1. Tìm theo Khóa chính (Primary Key)
    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")

    # 2. Lấy tất cả danh sách
    everyone = db.session.execute(db.select(Student)).scalars().all()
    lines.append(f"3. Tất cả: {len(everyone)} sinh viên")

    # 3. Lọc có điều kiện (gpa >= 8) và sắp xếp giảm dần
    stmt = (db.select(Student)
            .where(Student.gpa >= 8)
            .order_by(Student.gpa.desc()))
    good = db.session.execute(stmt).scalars().all()
    lines.append(f"4. Điểm >= 8: {good}")

    # 4. Tìm kiếm theo thuộc tính cụ thể bằng filter_by
    binh = db.session.scalar(db.select(Student).filter_by(mssv="23T1020002"))
    lines.append(f"5. MSSV 23T1020002: {binh}")

    # 5. Sử dụng hàm tổng hợp (count, avg)
    count = db.session.scalar(db.select(func.count(Student.id)))
    avg = db.session.scalar(db.select(func.avg(Student.gpa)))
    lines.append(f"6. Số SV: {count}, điểm TB: {avg:.2f}")

    return "\n".join(lines), TEXT

# ==========================================
# ROUTE BỔ SUNG: HIỂN THỊ KẾT QUẢ + BẢNG
# ==========================================
@app.get("/ket-qua-truy-van")
def query_and_display_table():
    count = db.session.scalar(db.select(func.count(Student.id)))
    if count == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước."

    sv_3 = db.session.get(Student, 3)
    sv_99 = db.session.get(Student, 99)
    everyone = db.session.scalars(db.select(Student)).all()

    stmt = db.select(Student).where(Student.gpa >= 8).order_by(Student.gpa.desc())
    good = db.session.scalars(stmt).all()

    binh = db.session.scalar(db.select(Student).filter_by(mssv="23T1020002"))
    avg = db.session.scalar(db.select(func.avg(Student.gpa)))

    return render_template(
        "truy_van.html",
        sv_3=sv_3,
        sv_99=sv_99,
        everyone=everyone,
        good=good,
        binh=binh,
        count=count,
        avg=avg
    )

if __name__ == '__main__':
    app.run(debug=True)