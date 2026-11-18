import os
from app import app
from models import db, Category, Book

ICON_CLEANCODE = '''
<g transform="translate(200, 140)">
  <text x="-34" y="16" font-family="Consolas, monospace" font-size="54" font-weight="bold" fill="#93c5fd" text-anchor="middle">{</text>
  <circle cx="0" cy="0" r="22" fill="#22c55e"/>
  <path d="M-9,0 L-3,7 L10,-7" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="34" y="16" font-family="Consolas, monospace" font-size="54" font-weight="bold" fill="#93c5fd" text-anchor="middle">}</text>
</g>'''

ICON_NETWORK = '''
<g transform="translate(200, 140)">
  <line x1="0" y1="-26" x2="-30" y2="22" stroke="#a7f3d0" stroke-width="3.5"/>
  <line x1="0" y1="-26" x2="30" y2="22" stroke="#a7f3d0" stroke-width="3.5"/>
  <line x1="-30" y1="22" x2="30" y2="22" stroke="#a7f3d0" stroke-width="3.5"/>
  <circle cx="0" cy="-26" r="12" fill="#ffffff"/>
  <circle cx="-30" cy="22" r="12" fill="#6ee7b7"/>
  <circle cx="30" cy="22" r="12" fill="#6ee7b7"/>
</g>'''

ICON_PROGIT = '''
<g transform="translate(200, 140)">
  <line x1="-22" y1="-32" x2="-22" y2="32" stroke="#ffffff" stroke-width="4"/>
  <path d="M-22,12 C-22,-6 22,-4 22,-22" fill="none" stroke="#fed7aa" stroke-width="4"/>
  <circle cx="-22" cy="-26" r="8" fill="#ffffff"/>
  <circle cx="-22" cy="24" r="8" fill="#ffffff"/>
  <circle cx="22" cy="-22" r="8" fill="#fdba74"/>
</g>'''

ICON_DATABASE = '''
<g transform="translate(200, 140)">
  <ellipse cx="0" cy="-24" rx="34" ry="12" fill="#e9d5ff" stroke="#ffffff" stroke-width="3"/>
  <path d="M-34,-24 L-34,24 C-34,31 34,31 34,24 L34,-24" fill="none" stroke="#ffffff" stroke-width="3"/>
  <path d="M-34,-8 C-34,-1 34,-1 34,-8" fill="none" stroke="#ffffff" stroke-width="3"/>
  <path d="M-34,8 C-34,15 34,15 34,8" fill="none" stroke="#ffffff" stroke-width="3"/>
</g>'''

ICON_FLASK = '''
<g transform="translate(200, 140)">
  <path d="M-14,-48 L14,-48 M-10,-48 L-10,-22 L-38,32 C-41,38 -37,44 -30,44 L30,44 C37,44 41,38 38,32 L10,-22 L10,-48"
        fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M-24,12 L24,12 L34,31 C36,35 33,39 28,39 L-28,39 C-33,39 -36,35 -34,31 Z"
        fill="#38bdf8" opacity="0.9"/>
  <text x="0" y="31" font-family="Consolas, monospace" font-size="16" font-weight="bold" fill="#0f172a" text-anchor="middle">&lt;/&gt;</text>
  <circle cx="-6" cy="-4" r="3.5" fill="#38bdf8"/>
  <circle cx="7" cy="-14" r="2.5" fill="#7dd3fc"/>
</g>'''

ICON_PYTHON = '''
<g transform="translate(200, 140)">
  <rect x="-48" y="-36" width="96" height="72" rx="10" fill="#0f172a" stroke="#facc15" stroke-width="3"/>
  <circle cx="-34" cy="-23" r="3.5" fill="#ef4444"/>
  <circle cx="-23" cy="-23" r="3.5" fill="#facc15"/>
  <circle cx="-12" cy="-23" r="3.5" fill="#22c55e"/>
  <line x1="-48" y1="-12" x2="48" y2="-12" stroke="#334155" stroke-width="2"/>
  <text x="-36" y="10" font-family="Consolas, monospace" font-size="17" font-weight="bold" fill="#facc15">&gt;&gt;&gt; py</text>
  <rect x="-36" y="19" width="48" height="4" rx="2" fill="#38bdf8"/>
  <rect x="16" y="19" width="18" height="4" rx="2" fill="#94a3b8"/>
</g>'''

SAMPLE_BOOKS = [
    {
        'cover': 'cover_cleancode.svg',
        'c1': '#1e3a8a', 'c2': '#3b82f6', 'icon': ICON_CLEANCODE,
        'title': 'Clean Code', 'author': 'Robert C. Martin',
        'publisher': 'Prentice Hall', 'publish_year': 2008,
        'price': 180000, 'stock': 5, 'category': 'Kỹ năng lập trình',
        'description': 'Cẩm nang viết mã sạch dành cho lập trình viên chuyên nghiệp.'
    },
    {
        'cover': 'cover_network.svg',
        'c1': '#065f46', 'c2': '#10b981', 'icon': ICON_NETWORK,
        'title': 'Mạng máy tính', 'author': 'Lê Văn C',
        'publisher': 'NXB Đại học Huế', 'publish_year': 2023,
        'price': 110000, 'stock': 12, 'category': 'Mạng',
        'description': 'Giáo trình nguyên lý mạng máy tính và các giao thức TCP/IP.'
    },
    {
        'cover': 'cover_progit.svg',
        'c1': '#9a3412', 'c2': '#f97316', 'icon': ICON_PROGIT,
        'title': 'Pro Git', 'author': 'Scott Chacon',
        'publisher': 'Apress', 'publish_year': 2014,
        'price': 150000, 'stock': 15, 'category': 'Công cụ',
        'description': 'Hướng dẫn sử dụng Git từ cơ bản đến nâng cao.'
    },
    {
        'cover': 'cover_database.svg',
        'c1': '#581c87', 'c2': '#a855f7', 'icon': ICON_DATABASE,
        'title': 'Cơ sở dữ liệu', 'author': 'Trần Văn B',
        'publisher': 'NXB Đại học Huế', 'publish_year': 2022,
        'price': 85000, 'stock': 0, 'category': 'Cơ sở dữ liệu',
        'description': 'Mô hình quan hệ, đại số quan hệ và chuẩn hoá dữ liệu.'
    },
    {
        'cover': 'cover_flask.svg',
        'c1': '#0f172a', 'c2': '#334155', 'icon': ICON_FLASK,
        'title': 'Giáo trình Flask', 'author': 'Miguel Grinberg',
        'publisher': 'O’Reilly', 'publish_year': 2024,
        'price': 120000, 'stock': 20, 'category': 'Lập trình',
        'description': 'Phát triển ứng dụng web với Python Flask.'
    },
    {
        'cover': 'cover_python.svg',
        'c1': '#1e3a8a', 'c2': '#2563eb', 'icon': ICON_PYTHON,
        'title': 'Lập trình Python cơ bản', 'author': 'Nguyễn Văn A',
        'publisher': 'NXB Đại học Huế', 'publish_year': 2024,
        'price': 95000, 'stock': 30, 'category': 'Lập trình',
        'description': 'Nhập môn lập trình Python cho sinh viên Công nghệ Thông tin.'
    },
]

def generate_sample_covers(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)
    for item in SAMPLE_BOOKS:
        pub_info = f"{item['publisher']}, {item['publish_year']}"
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="520" viewBox="0 0 400 520">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{item['c1']}"/>
      <stop offset="100%" stop-color="{item['c2']}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="520" rx="14" fill="url(#bg)"/>
  <rect x="24" y="24" width="352" height="472" rx="10" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>
  {item['icon']}
  <text x="200" y="255" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#ffffff" text-anchor="middle">{item['title']}</text>
  <line x1="110" y1="285" x2="290" y2="285" stroke="rgba(255,255,255,0.5)" stroke-width="2"/>
  <text x="200" y="325" font-family="Arial, sans-serif" font-size="18" fill="#f1f5f9" text-anchor="middle">{item['author']}</text>
  <text x="200" y="455" font-family="Arial, sans-serif" font-size="15" fill="rgba(255,255,255,0.85)" text-anchor="middle">{pub_info}</text>
</svg>'''
        with open(os.path.join(upload_dir, item['cover']), 'w', encoding='utf-8') as f:
            f.write(svg)

with app.app_context():
    db.create_all()
    generate_sample_covers(app.config['UPLOAD_FOLDER'])

    if Category.query.count() == 0:
        cats = {
            'Lập trình': Category(name='Lập trình', description='Sách lập trình căn bản và nâng cao'),
            'Cơ sở dữ liệu': Category(name='Cơ sở dữ liệu', description='Hệ quản trị CSDL'),
            'Công cụ': Category(name='Công cụ', description='Git, Docker, Linux'),
            'Mạng': Category(name='Mạng', description='Mạng máy tính và bảo mật'),
            'Kỹ năng lập trình': Category(name='Kỹ năng lập trình', description='Clean Code, Refactoring'),
            'Thiết kế': Category(name='Thiết kế', description='UI/UX, Thiết kế hệ thống'),
        }
        db.session.add_all(cats.values())
        db.session.flush()

        for item in SAMPLE_BOOKS:
            db.session.add(Book(
                title=item['title'],
                author=item['author'],
                publisher=item['publisher'],
                publish_year=item['publish_year'],
                price=item['price'],
                stock=item['stock'],
                category_id=cats[item['category']].id,
                cover_image=item['cover'],
                description=item['description']
            ))
        db.session.commit()
        print('Đã nạp dữ liệu mẫu và ảnh bìa mới thành công!')
    else:
        title_to_cover = {item['title']: item['cover'] for item in SAMPLE_BOOKS}
        for b in Book.query.all():
            if not b.cover_image and b.title in title_to_cover:
                b.cover_image = title_to_cover[b.title]
        db.session.commit()
        print('Đã cập nhật NXB và năm xuất bản lên ảnh bìa!')