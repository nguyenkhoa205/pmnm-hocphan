import os
import uuid
from datetime import datetime, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session
)
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from sqlalchemy import func, or_, extract

from config import Config
from models import db, Category, Book, Order, OrderItem, OrderStatusHistory
from forms import CheckoutForm, BookForm, CategoryForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# ======================== TIỆN ÍCH & CONTEXT PROCESSOR ========================

@app.template_filter('vnd')
def format_vnd(value):
    if value is None:
        return '0 ₫'
    return f"{int(value):,}".replace(',', '.') + ' ₫'

@app.template_filter('num_fmt')
def format_num(value):
    if value is None:
        return '0'
    return f"{int(value):,}".replace(',', '.')

def get_cart():
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
    return cart

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def build_cart_details():
    """Luôn lấy giá mới nhất từ CSDL, không lưu giá trong session."""
    cart = get_cart()
    items = []
    subtotal = 0
    total_qty = 0
    cleaned_cart = {}

    for book_id_str, qty in cart.items():
        book = db.session.get(Book, int(book_id_str))
        if book and qty > 0:
            cleaned_cart[book_id_str] = qty
            line_total = book.price * qty
            subtotal += line_total
            total_qty += qty
            items.append({
                'book': book,
                'quantity': qty,
                'line_total': line_total
            })

    if cleaned_cart != cart:
        save_cart(cleaned_cart)

    shipping_fee = 0 if (subtotal >= 200000 or subtotal == 0) else 20000
    grand_total = subtotal + shipping_fee
    return items, subtotal, shipping_fee, grand_total, total_qty

@app.context_processor
def inject_global_badges():
    cart = get_cart()
    cart_total_qty = sum(int(q) for q in cart.values()) if cart else 0
    pending_orders_badge = (
        db.session.query(func.count(Order.id))
        .filter(Order.status == 'Chờ xác nhận')
        .scalar() or 0
    )
    return dict(
        cart_total_qty=cart_total_qty,
        pending_orders_badge=pending_orders_badge
    )

def save_uploaded_cover(file_storage):
    ext = os.path.splitext(secure_filename(file_storage.filename))[1].lower()
    random_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
    file_storage.save(file_path)
    return random_name

def remove_cover_file(filename):
    if filename:
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)

# ======================== PHẦN A: TRANG BÁN HÀNG ========================

@app.route('/')
def index():
    return redirect(url_for('book_list'))

# Màn hình 1: Danh sách sách (/books)
@app.route('/books')
def book_list():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)

    query = Book.query
    if q:
        keyword = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(keyword), Book.author.ilike(keyword)))
    if category_id:
        query = query.filter(Book.category_id == category_id)

    books = query.order_by(Book.id.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'shop/books.html',
        books=books,
        categories=categories,
        q=q,
        selected_category=category_id
    )

# Màn hình 2: Chọn sách (/books/<id>)
@app.route('/books/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    cart = get_cart()
    in_cart = cart.get(str(book.id), 0)
    max_addable = max(0, book.stock - in_cart)
    return render_template(
        'shop/book_detail.html',
        book=book,
        in_cart=in_cart,
        max_addable=max_addable
    )

# Thêm sách vào giỏ hàng
@app.route('/cart/add/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    next_url = request.form.get('next') or url_for('book_list')

    try:
        qty = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        flash('Số lượng không hợp lệ.', 'danger')
        return redirect(next_url)

    cart = get_cart()
    in_cart = cart.get(str(book.id), 0)
    max_addable = book.stock - in_cart

    if qty < 1 or qty > max_addable:
        flash(f'Số lượng không hợp lệ (tối đa có thể thêm {max(0, max_addable)} cuốn).', 'danger')
        return redirect(next_url)

    cart[str(book.id)] = in_cart + qty
    save_cart(cart)
    flash(f'Đã thêm {qty} × {book.title} vào giỏ hàng.', 'success')
    return redirect(next_url)

# Màn hình 3: Giỏ hàng (/cart)
@app.route('/cart')
def view_cart():
    items, subtotal, shipping_fee, grand_total, total_qty = build_cart_details()
    return render_template(
        'shop/cart.html',
        items=items,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        grand_total=grand_total
    )

@app.route('/cart/update/<int:book_id>', methods=['POST'])
def update_cart_item(book_id):
    book = Book.query.get_or_404(book_id)
    action = request.form.get('action')
    cart = get_cart()
    key = str(book.id)

    if key in cart:
        if action == 'increase':
            if cart[key] < book.stock:
                cart[key] += 1
        elif action == 'decrease':
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]
        save_cart(cart)

    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:book_id>', methods=['POST'])
def remove_cart_item(book_id):
    cart = get_cart()
    key = str(book_id)
    if key in cart:
        del cart[key]
        save_cart(cart)
        flash('Đã xoá sách khỏi giỏ hàng.', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    save_cart({})
    flash('Đã xoá toàn bộ giỏ hàng.', 'info')
    return redirect(url_for('view_cart'))

# Màn hình 4: Thông tin khách hàng (/checkout)
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    items, subtotal, shipping_fee, grand_total, total_qty = build_cart_details()
    if not items:
        flash('Giỏ hàng đang trống. Vui lòng chọn sách trước khi đặt hàng.', 'warning')
        return redirect(url_for('view_cart'))

    form = CheckoutForm()
    if form.validate_on_submit():
        insufficient = []
        for item in items:
            fresh_book = db.session.get(Book, item['book'].id)
            if not fresh_book or fresh_book.stock < item['quantity']:
                avail = fresh_book.stock if fresh_book else 0
                insufficient.append(f'"{item["book"].title}" (chỉ còn {avail} cuốn)')

        if insufficient:
            flash('Không đủ tồn kho cho sách: ' + ', '.join(insufficient) + '.', 'danger')
            return redirect(url_for('view_cart'))

        now = datetime.now()
        order = Order(
            customer_name=form.customer_name.data.strip(),
            customer_phone=form.customer_phone.data.strip(),
            customer_email=form.customer_email.data.strip() if form.customer_email.data else None,
            shipping_address=form.shipping_address.data.strip(),
            note=form.note.data.strip() if form.note.data else None,
            payment_method=form.payment_method.data,
            shipping_fee=shipping_fee,
            total_amount=grand_total,
            status='Chờ xác nhận',
            created_at=now
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            fresh_book = db.session.get(Book, item['book'].id)
            order_item = OrderItem(
                order_id=order.id,
                book_id=fresh_book.id,
                quantity=item['quantity'],
                unit_price=fresh_book.price
            )
            fresh_book.stock -= item['quantity']
            db.session.add(order_item)

        history = OrderStatusHistory(
            order_id=order.id,
            status='Chờ xác nhận',
            changed_at=now
        )
        db.session.add(history)
        db.session.commit()

        save_cart({})
        flash(f'Đặt hàng thành công! Mã đơn hàng của bạn là #{order.id}.', 'success')
        return redirect(url_for('order_success', order_id=order.id))

    return render_template(
        'shop/checkout.html',
        form=form,
        items=items,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        grand_total=grand_total
    )

# Màn hình 5: Đặt hàng thành công (/orders/<id>)
@app.route('/orders/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    subtotal = sum(item.unit_price * item.quantity for item in order.items)
    return render_template('shop/order_success.html', order=order, subtotal=subtotal)

# ======================== PHẦN B: TRANG QUẢN TRỊ ========================

# Màn hình 6: Tổng quan (/admin)
@app.route('/admin')
def admin_dashboard():
    now = datetime.now()

    total_books = db.session.query(func.count(Book.id)).scalar() or 0
    pending_orders = (
        db.session.query(func.count(Order.id))
        .filter(Order.status == 'Chờ xác nhận')
        .scalar() or 0
    )
    monthly_revenue = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(
            Order.status == 'Hoàn tất',
            extract('year', Order.created_at) == now.year,
            extract('month', Order.created_at) == now.month
        )
        .scalar() or 0
    )
    low_stock_count = (
        db.session.query(func.count(Book.id))
        .filter(Book.stock <= 5)
        .scalar() or 0
    )

    latest_orders = Order.query.order_by(Order.created_at.desc(), Order.id.desc()).limit(5).all()
    low_stock_books = Book.query.filter(Book.stock <= 5).order_by(Book.stock.asc()).all()

    chart_days = []
    max_day_rev = 1
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_rev = (
            db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
            .filter(
                Order.status == 'Hoàn tất',
                func.date(Order.created_at) == day
            )
            .scalar() or 0
        )
        if day_rev > max_day_rev:
            max_day_rev = day_rev
        chart_days.append({'label': day.strftime('%d/%m'), 'revenue': day_rev})

    return render_template(
        'admin/dashboard.html',
        current_month=now.month,
        total_books=total_books,
        pending_orders=pending_orders,
        monthly_revenue=monthly_revenue,
        low_stock_count=low_stock_count,
        latest_orders=latest_orders,
        low_stock_books=low_stock_books,
        chart_days=chart_days,
        max_day_rev=max_day_rev
    )

# Màn hình 7: Quản lý sách (/admin/books)
@app.route('/admin/books')
def admin_books():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    stock_filter = request.args.get('stock_filter', '').strip()

    query = Book.query
    if q:
        kw = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(kw), Book.author.ilike(kw)))
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if stock_filter == 'in_stock':
        query = query.filter(Book.stock > 5)
    elif stock_filter == 'low_stock':
        query = query.filter(Book.stock > 0, Book.stock <= 5)
    elif stock_filter == 'out_of_stock':
        query = query.filter(Book.stock == 0)

    pagination = query.order_by(Book.id.desc()).paginate(page=page, per_page=5, error_out=False)
    categories = Category.query.order_by(Category.name.asc()).all()

    ordered_book_ids = {
        row[0] for row in db.session.query(OrderItem.book_id).distinct().all()
    }

    return render_template(
        'admin/books.html',
        pagination=pagination,
        books=pagination.items,
        categories=categories,
        q=q,
        selected_category=category_id,
        stock_filter=stock_filter,
        ordered_book_ids=ordered_book_ids
    )

# Màn hình 8: Thêm và sửa sách
@app.route('/admin/books/new', methods=['GET', 'POST'])
def admin_book_new():
    form = BookForm()
    if form.validate_on_submit():
        cover_filename = None
        if isinstance(form.cover_image.data, FileStorage) and form.cover_image.data.filename:
            cover_filename = save_uploaded_cover(form.cover_image.data)

        book = Book(
            title=form.title.data.strip(),
            author=form.author.data.strip(),
            publisher=form.publisher.data.strip() if form.publisher.data else 'NXB Đại học Huế',
            category_id=form.category_id.data,
            publish_year=form.publish_year.data,
            price=form.price.data,
            stock=form.stock.data,
            description=form.description.data.strip() if form.description.data else None,
            cover_image=cover_filename
        )
        db.session.add(book)
        db.session.commit()
        flash(f'Đã thêm sách "{book.title}".', 'success')
        return redirect(url_for('admin_books'))

    return render_template('admin/book_form.html', form=form, book=None)

@app.route('/admin/books/<int:book_id>/edit', methods=['GET', 'POST'])
def admin_book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(book_id=book.id, obj=book)

    if form.validate_on_submit():
        book.title = form.title.data.strip()
        book.author = form.author.data.strip()
        book.publisher = form.publisher.data.strip() if form.publisher.data else 'NXB Đại học Huế'
        book.category_id = form.category_id.data
        book.publish_year = form.publish_year.data
        book.price = form.price.data
        book.stock = form.stock.data
        book.description = form.description.data.strip() if form.description.data else None

        if isinstance(form.cover_image.data, FileStorage) and form.cover_image.data.filename:
            old_cover = book.cover_image
            book.cover_image = save_uploaded_cover(form.cover_image.data)
            remove_cover_file(old_cover)

        db.session.commit()
        flash(f'Đã cập nhật sách "{book.title}".', 'success')
        return redirect(url_for('admin_books'))

    return render_template('admin/book_form.html', form=form, book=book)

@app.route('/admin/books/<int:book_id>/delete', methods=['POST'])
def admin_book_delete(book_id):
    book = Book.query.get_or_404(book_id)
    has_orders = db.session.query(OrderItem.id).filter_by(book_id=book.id).first() is not None
    if has_orders:
        flash(f'Không thể xoá "{book.title}": sách đã có trong đơn hàng.', 'danger')
        return redirect(url_for('admin_books'))

    remove_cover_file(book.cover_image)
    db.session.delete(book)
    db.session.commit()
    flash(f'Đã xoá sách "{book.title}".', 'success')
    return redirect(url_for('admin_books'))

# Màn hình 9: Danh mục sách (/admin/categories)
@app.route('/admin/categories', methods=['GET', 'POST'])
def admin_categories():
    edit_id = request.args.get('edit_id', type=int)
    editing_category = Category.query.get_or_404(edit_id) if edit_id else None

    form = CategoryForm(
        category_id=editing_category.id if editing_category else None,
        obj=editing_category
    )

    if form.validate_on_submit():
        if editing_category:
            editing_category.name = form.name.data.strip()
            editing_category.description = form.description.data.strip() if form.description.data else None
            db.session.commit()
            flash(f'Đã cập nhật danh mục "{editing_category.name}".', 'success')
        else:
            cat = Category(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None
            )
            db.session.add(cat)
            db.session.commit()
            flash(f'Đã thêm danh mục "{cat.name}".', 'success')
        return redirect(url_for('admin_categories'))

    categories_data = (
        db.session.query(Category, func.count(Book.id).label('book_count'))
        .outerjoin(Book, Category.id == Book.category_id)
        .group_by(Category.id)
        .order_by(Category.id.asc())
        .all()
    )

    return render_template(
        'admin/categories.html',
        categories_data=categories_data,
        form=form,
        editing_category=editing_category
    )

@app.route('/admin/categories/<int:cat_id>/delete', methods=['POST'])
def admin_category_delete(cat_id):
    category = Category.query.get_or_404(cat_id)
    book_count = db.session.query(func.count(Book.id)).filter_by(category_id=category.id).scalar() or 0
    if book_count > 0:
        flash(f'Không thể xoá "{category.name}": còn {book_count} sách.', 'danger')
        return redirect(url_for('admin_categories'))

    db.session.delete(category)
    db.session.commit()
    flash(f'Đã xoá danh mục "{category.name}".', 'success')
    return redirect(url_for('admin_categories'))

# Màn hình 10: Danh sách đơn hàng (/admin/orders)
@app.route('/admin/orders')
def admin_orders():
    status = request.args.get('status', '').strip()
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    status_rows = (
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    status_counts = dict(status_rows)
    total_all_orders = sum(status_counts.values())

    query = Order.query
    if status:
        query = query.filter(Order.status == status)
    if q:
        clean_id = q.lstrip('#')
        conditions = [
            Order.customer_name.ilike(f"%{q}%"),
            Order.customer_phone.ilike(f"%{q}%")
        ]
        if clean_id.isdigit():
            conditions.append(Order.id == int(clean_id))
        query = query.filter(or_(*conditions))

    filtered_count = query.count()
    filtered_total_value = (
        query.with_entities(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
    )

    pagination = query.order_by(Order.created_at.desc(), Order.id.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template(
        'admin/orders.html',
        pagination=pagination,
        orders=pagination.items,
        status=status,
        q=q,
        status_counts=status_counts,
        total_all_orders=total_all_orders,
        filtered_count=filtered_count,
        filtered_total_value=filtered_total_value
    )

# Màn hình 11: Chi tiết đơn hàng (/admin/orders/<id>)
VALID_TRANSITIONS = {
    'Chờ xác nhận': ['Đang giao', 'Đã huỷ'],
    'Đang giao': ['Hoàn tất', 'Đã huỷ'],
    'Hoàn tất': [],
    'Đã huỷ': [],
}

@app.route('/admin/orders/<int:order_id>', methods=['GET', 'POST'])
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    allowed_next = VALID_TRANSITIONS.get(order.status, [])

    if request.method == 'POST':
        new_status = request.form.get('new_status', '').strip()
        if new_status not in allowed_next:
            flash('Chuyển trạng thái không hợp lệ.', 'danger')
            return redirect(url_for('admin_order_detail', order_id=order.id))

        if new_status == 'Đã huỷ':
            for item in order.items:
                item.book.stock += item.quantity

        order.status = new_status
        history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
            changed_at=datetime.now()
        )
        db.session.add(history)
        db.session.commit()
        flash(f'Đã cập nhật trạng thái đơn #{order.id} sang "{new_status}".', 'success')
        return redirect(url_for('admin_order_detail', order_id=order.id))

    next_select_options = [s for s in allowed_next if s != 'Đã huỷ']
    can_cancel = 'Đã huỷ' in allowed_next

    return render_template(
        'admin/order_detail.html',
        order=order,
        next_select_options=next_select_options,
        can_cancel=can_cancel
    )

if __name__ == '__main__':
    app.run(debug=True)