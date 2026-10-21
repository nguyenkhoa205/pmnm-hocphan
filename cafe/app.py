import math  
from datetime import datetime
from flask import (  
    Flask,
    abort,
    render_template,
    request,
)

app = Flask(__name__)

SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê lợi, Huế",
    "open": 7,
    "close": 22,
}
PROMOTIONS = ["Giảm 10% cho sinh viên", "Mua 2 tặng 1 vào thứ Hai"]
MENU = [
    {"name": "Cà phê sữa", "price": 20000, "available": True},
    {"name": "Cà phê đen", "price": 15000, "available": False},
    {"name": "Trà đào", "price": 25000, "available": False},
    {"name": "Bánh mì", "price": 10000, "available": True},
    {"name": "Bánh ngọt", "price": 15000, "available": True},
]


@app.template_filter("vnd")
def vnd_filter(value):
    try:
        return f"{int(value):,} đ".replace(",", ".")
    except (ValueError, TypeError):
        return f"{value} đ"


@app.route("/")
def index():
    hour = request.args.get("gio", type=int)
    if hour is None:
        hour = datetime.now().hour
    is_open = SHOP["open"] <= hour < SHOP["close"]
    return render_template(
        "index.html",
        shop=SHOP,
        hour=hour,
        is_open=is_open,
        promotions=PROMOTIONS,
    )


@app.route("/menu")
def menu():
    page_param = request.args.get("page", 1)
    try:
        page = int(page_param)
    except (ValueError, TypeError):
        abort(404)

    per_page = 3
    total_items = len(MENU)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    if page < 1 or page > total_pages:
        abort(404)

    start = (page - 1) * per_page
    end = start + per_page
    items_on_page = MENU[start:end]

    return render_template(
        "menu.html",
        shop=SHOP,
        menu=items_on_page,
        page=page,
        pages=total_pages,
        total_items=total_items,
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", shop=SHOP)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", shop=SHOP), 404


if __name__ == "__main__":
    app.run(debug=True)