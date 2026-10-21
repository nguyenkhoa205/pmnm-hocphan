from datetime import datetime
from flask import Flask, app, render_template, request

app = Flask(__name__)

SHOP = {"name": "Cà phê Sông Hương",
        "address": "12 Lê lợi, Huế", 
        "open": 7, "close": 22}
PROMOTIONS = [
    "Giảm 10% cho sinh viên", 
    "Mua 2 tặng 1 vào thứ Hai"]
MENU = [
    {"name": "Cà phê sữa", "price": 20000, "available": True},
    {"name": "Cà phê đen", "price": 15000, "available": False},
    {"name": "Trà đào", "price": 25000, "available": False},
    {"name": "Bánh mì", "price": 10000, "available": True},
    {"name": "Bánh ngọt", "price": 15000, "available": True}
]
@app.route("/")
def index():
    hour = request.args.get("gio", type=int)
    if hour is None:
        hour = datetime.now().hour
    is_open = SHOP["open"] <= hour < SHOP["close"]
    return render_template("index.html", shop=SHOP, 
        hour=hour, is_open=is_open,
        promotions=PROMOTIONS)
@app .route("/menu")
def menu():
    return render_template("menu.html",shop=SHOP,  menu=MENU)

if __name__ == "__main__":
    app.run(debug=True) 