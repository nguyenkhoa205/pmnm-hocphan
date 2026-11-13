import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'khoa_bi_mat_bai_kiem_tra'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')


@app.route('/')
def index():
    return redirect(url_for('manage_categories'))


# =========================================================
# 1. CRUD DANH MỤC SÁCH
# =========================================================
@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    conn = get_db_connection()

    if request.method == 'POST':
        cat_id = request.form.get('id')
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Tên danh mục không được để trống!', 'danger')
        else:
            try:
                if cat_id:  # Update
                    conn.execute(
                        'UPDATE categories SET name = ?, description = ? WHERE id = ?',
                        (name, description, cat_id)
                    )
                    flash('Cập nhật danh mục thành công!', 'success')
                else:       # Create
                    conn.execute(
                        'INSERT INTO categories (name, description) VALUES (?, ?)',
                        (name, description)
                    )
                    flash('Thêm danh mục mới thành công!', 'success')
                conn.commit()
            except sqlite3.IntegrityError:
                flash('Tên danh mục đã tồn tại!', 'danger')

        conn.close()
        return redirect(url_for('manage_categories'))

    edit_id = request.args.get('edit_id')
    edit_category = None
    if edit_id:
        edit_category = conn.execute('SELECT * FROM categories WHERE id = ?', (edit_id,)).fetchone()

    # Read danh sách danh mục
    categories = conn.execute('''
        SELECT c.*, COUNT(b.id) AS book_count
        FROM categories c
        LEFT JOIN books b ON c.id = b.category_id
        GROUP BY c.id
        ORDER BY c.id ASC
    ''').fetchall()

    conn.close()
    return render_template('categories.html', categories=categories, edit_category=edit_category)


@app.route('/categories/delete/<int:id>', methods=['POST'])
def delete_category(id):
    conn = get_db_connection()
    book_count = conn.execute('SELECT COUNT(*) FROM books WHERE category_id = ?', (id,)).fetchone()[0]
    if book_count > 0:
        flash(f'Không thể xóa danh mục này vì đang có {book_count} cuốn sách bên trong!', 'danger')
    else:
        conn.execute('DELETE FROM categories WHERE id = ?', (id,))
        conn.commit()
        flash('Đã xóa danh mục thành công!', 'success')
    conn.close()
    return redirect(url_for('manage_categories'))


# =========================================================
# 2. CRUD SÁCH THEO DANH MỤC
# =========================================================
@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    conn = get_db_connection()
    selected_category_id = request.args.get('category_id', type=int)

    if request.method == 'POST':
        book_id = request.form.get('id')
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        price = request.form.get('price', 0, type=float)
        quantity = request.form.get('quantity', 0, type=int)
        category_id = request.form.get('category_id', type=int)
        filter_cat = request.form.get('filter_cat', type=int)

        if not title or not author or not category_id:
            flash('Vui lòng nhập đầy đủ Tên sách, Tác giả và chọn Danh mục!', 'danger')
        else:
            if book_id:  # Update
                conn.execute('''
                    UPDATE books
                    SET title = ?, author = ?, price = ?, quantity = ?, category_id = ?
                    WHERE id = ?
                ''', (title, author, price, quantity, category_id, book_id))
                flash('Cập nhật thông tin sách thành công!', 'success')
            else:        # Create
                conn.execute('''
                    INSERT INTO books (title, author, price, quantity, category_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, author, price, quantity, category_id))
                flash('Thêm sách mới thành công!', 'success')
            conn.commit()

        conn.close()
        if filter_cat:
            return redirect(url_for('manage_books', category_id=filter_cat))
        return redirect(url_for('manage_books'))

    categories = conn.execute('SELECT * FROM categories ORDER BY name ASC').fetchall()

    edit_id = request.args.get('edit_id', type=int)
    edit_book = None
    if edit_id:
        edit_book = conn.execute('SELECT * FROM books WHERE id = ?', (edit_id,)).fetchone()

    # Read danh sách sách (lọc theo category_id nếu có)
    current_category = None
    if selected_category_id:
        current_category = conn.execute(
            'SELECT * FROM categories WHERE id = ?', (selected_category_id,)
        ).fetchone()
        books = conn.execute('''
            SELECT b.*, c.name AS category_name
            FROM books b
            JOIN categories c ON b.category_id = c.id
            WHERE b.category_id = ?
            ORDER BY b.id DESC
        ''', (selected_category_id,)).fetchall()
    else:
        books = conn.execute('''
            SELECT b.*, c.name AS category_name
            FROM books b
            JOIN categories c ON b.category_id = c.id
            ORDER BY b.id DESC
        ''').fetchall()

    conn.close()
    return render_template(
        'books.html',
        books=books,
        categories=categories,
        selected_category_id=selected_category_id,
        current_category=current_category,
        edit_book=edit_book
    )


@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    filter_cat = request.form.get('filter_cat', type=int)
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Đã xóa sách thành công!', 'success')

    if filter_cat:
        return redirect(url_for('manage_books', category_id=filter_cat))
    return redirect(url_for('manage_books'))


# =========================================================
# 3. DASHBOARD QUẢN LÝ DANH MỤC SÁCH VÀ SÁCH
# =========================================================
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()

    total_categories = conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    total_books = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    total_quantity = conn.execute('SELECT COALESCE(SUM(quantity), 0) FROM books').fetchone()[0]

    category_stats = conn.execute('''
        SELECT c.id, c.name, c.description,
               COUNT(b.id) AS book_count,
               COALESCE(SUM(b.quantity), 0) AS total_qty
        FROM categories c
        LEFT JOIN books b ON c.id = b.category_id
        GROUP BY c.id
        ORDER BY c.id ASC
    ''').fetchall()

    recent_books = conn.execute('''
        SELECT b.*, c.name AS category_name
        FROM books b
        JOIN categories c ON b.category_id = c.id
        ORDER BY b.id DESC
        LIMIT 5
    ''').fetchall()

    conn.close()
    return render_template(
        'dashboard.html',
        total_categories=total_categories,
        total_books=total_books,
        total_quantity=total_quantity,
        category_stats=category_stats,
        recent_books=recent_books
    )


# =========================================================
# 4. CSDL SQLITE (KẾT NỐI & KHỞI TẠO BẢNG)
# =========================================================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0,
            quantity INTEGER NOT NULL DEFAULT 0,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    count = cursor.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    if count == 0:
        cursor.executemany(
            'INSERT INTO categories (name, description) VALUES (?, ?)',
            [
                ('Công nghệ thông tin', 'Sách lập trình, cơ sở dữ liệu và mạng máy tính'),
                ('Văn học', 'Tiểu thuyết, truyện ngắn trong và ngoài nước'),
                ('Kinh tế - Quản trị', 'Sách khởi nghiệp, tài chính và quản lý')
            ]
        )
        cursor.executemany(
            'INSERT INTO books (title, author, price, quantity, category_id) VALUES (?, ?, ?, ?, ?)',
            [
                ('Lập trình Python cơ bản', 'Nguyễn Văn An', 120000, 15, 1),
                ('Cơ sở dữ liệu SQLite', 'Trần Thị Bình', 95000, 10, 1),
                ('Nhà Giả Kim', 'Paulo Coelho', 79000, 25, 2),
                ('Đắc Nhân Tâm', 'Dale Carnegie', 86000, 30, 3)
            ]
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)