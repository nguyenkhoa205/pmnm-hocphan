from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.datastructures import FileStorage
from wtforms import StringField, TextAreaField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, InputRequired, Optional, Email, Regexp, NumberRange, ValidationError
from sqlalchemy import func
from models import Book, Category

class FileSizeLimit:
    """Kiểm tra dung lượng file tải lên tối đa (mặc định 2 MB)."""
    def __init__(self, max_mb=2):
        self.max_bytes = max_mb * 1024 * 1024
        self.max_mb = max_mb

    def __call__(self, form, field):
        if isinstance(field.data, FileStorage) and field.data.filename:
            field.data.seek(0, 2)
            size = field.data.tell()
            field.data.seek(0)
            if size > self.max_bytes:
                raise ValidationError(f'Kích thước ảnh tối đa {self.max_mb} MB.')

class CheckoutForm(FlaskForm):
    customer_name = StringField('Họ tên', validators=[
        DataRequired(message='Vui lòng nhập họ tên.')
    ])
    customer_phone = StringField('Số điện thoại', validators=[
        DataRequired(message='Vui lòng nhập số điện thoại.'),
        Regexp(r'^0\d{9}$', message='Số điện thoại gồm 10 chữ số.')
    ])
    customer_email = StringField('Email', validators=[
        Optional(),
        Email(message='Email không đúng định dạng.')
    ])
    shipping_address = StringField('Địa chỉ giao hàng', validators=[
        DataRequired(message='Vui lòng nhập địa chỉ giao hàng.')
    ])
    note = StringField('Ghi chú', validators=[Optional()])
    payment_method = RadioField(
        'Thanh toán',
        choices=[
            ('Tiền mặt khi nhận hàng', 'Tiền mặt khi nhận hàng'),
            ('Chuyển khoản', 'Chuyển khoản')
        ],
        default='Tiền mặt khi nhận hàng',
        validators=[DataRequired()]
    )

class BookForm(FlaskForm):
    title = StringField('Tên sách', validators=[
        DataRequired(message='Tên sách là bắt buộc.')
    ])
    author = StringField('Tác giả', validators=[
        DataRequired(message='Tác giả là bắt buộc.')
    ])
    publisher = StringField('Nhà xuất bản', default='NXB Đại học Huế', validators=[Optional()])
    category_id = SelectField('Danh mục', coerce=int, validators=[
        DataRequired(message='Vui lòng chọn danh mục.')
    ])
    publish_year = IntegerField('Năm xuất bản', validators=[
        Optional(),
        NumberRange(min=1900, max=datetime.now().year,
                    message=f'Năm xuất bản từ 1900 đến {datetime.now().year}.')
    ])
    price = IntegerField('Giá (đồng)', validators=[
        DataRequired(message='Vui lòng nhập giá sách.'),
        NumberRange(min=1000, message='Giá sách tối thiểu 1.000 đ.')
    ])
    stock = IntegerField('Tồn kho', validators=[
        InputRequired(message='Vui lòng nhập số lượng tồn kho.'),
        NumberRange(min=0, message='Tồn kho không âm.')
    ])
    description = TextAreaField('Mô tả', validators=[Optional()])
    cover_image = FileField('Ảnh bìa', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Chỉ chấp nhận ảnh JPG, PNG, WEBP.'),
        FileSizeLimit(max_mb=2)
    ])

    def __init__(self, book_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.book_id = book_id
        self.category_id.choices = [
            (c.id, c.name) for c in Category.query.order_by(Category.name.asc()).all()
        ]

    def validate_title(self, field):
        query = Book.query.filter(func.lower(Book.title) == field.data.strip().lower())
        if self.book_id is not None:
            query = query.filter(Book.id != self.book_id)
        if query.first():
            raise ValidationError('Tên sách đã tồn tại.')

class CategoryForm(FlaskForm):
    name = StringField('Tên', validators=[
        DataRequired(message='Tên danh mục là bắt buộc.')
    ])
    description = TextAreaField('Mô tả', validators=[Optional()])

    def __init__(self, category_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_id = category_id

    def validate_name(self, field):
        query = Category.query.filter(func.lower(Category.name) == field.data.strip().lower())
        if self.category_id is not None:
            query = query.filter(Category.id != self.category_id)
        if query.first():
            raise ValidationError('Danh mục đã tồn tại.')