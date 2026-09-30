from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

BOOKS = [
    {
        "id": 1,
        "title": "Lập trình Python",
        "author": "Nguyễn Văn A",
        "year": 2024,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 2,
        "title": "Lập trình Java",
        "author": "Nguyễn Văn B",
        "year": 2023,
        "category": "Lập trình",
        "available": False
    },
    {
        "id": 3,
        "title": "Cơ sở dữ liệu",
        "author": "Nguyễn Văn C",
        "year": 2022,
        "category": "Cơ sở dữ liệu",
        "available": True
    },
    {
        "id": 4,
        "title": "Flask cơ bản",
        "author": "Nguyễn Văn D",
        "year": 2025,
        "category": "Lập trình",
        "available": True
    }
]


# =========================
# TRANG CHỦ
# =========================

@app.route("/")
def index():
    total_books = len(BOOKS)

    available_books = sum(
        1 for book in BOOKS
        if book["available"]
    )

    return render_template(
        "index.html",
        total_books=total_books,
        available_books=available_books
    )


# =========================
# DANH SÁCH SÁCH
# =========================

@app.route("/books")
def books():
    category = request.args.get("category")

    if category:
        filtered_books = [
            book for book in BOOKS
            if book["category"] == category
        ]
    else:
        filtered_books = BOOKS

    categories = sorted(
        set(book["category"] for book in BOOKS)
    )

    return render_template(
        "books.html",
        books=filtered_books,
        category=category,
        categories=categories
    )


# =========================
# CHI TIẾT SÁCH
# =========================

@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = next(
        (book for book in BOOKS if book["id"] == book_id),
        None
    )

    if book is None:
        return render_template(
            "404.html",
            message=f"Không có sách với ID = {book_id}"
        ), 404

    return render_template(
        "book_detail.html",
        book=book
    )


# =========================
# API - DANH SÁCH SÁCH
# =========================

@app.route("/api/books")
def api_books():
    return jsonify(BOOKS)


# =========================
# API - CHI TIẾT SÁCH
# =========================

@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = next(
        (book for book in BOOKS if book["id"] == book_id),
        None
    )

    if book is None:
        return jsonify({
            "error": f"Không có sách với ID = {book_id}"
        }), 404

    return jsonify(book)


# =========================
# TRANG 404
# =========================

@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "404.html",
        message="Trang bạn yêu cầu không tồn tại."
    ), 404


# =========================
# CHẠY ỨNG DỤNG
# =========================

if __name__ == "__main__":
    app.run(debug=True)