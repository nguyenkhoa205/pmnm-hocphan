from flask import Flask, request as req, url_for
app = Flask(__name__)

@app.route("/home")
@app.route("/index")
@app.route("/")
def index():
    return "<a href='/'>Trang chủ</a><a href='{url_for('gioi_thieu')}'>Giới thiệu</a><a href='/user/NguyenVanA'>User profile</a><a href='/square/5'>Square</a><a href='/square2/5.5'>Square2</a><a href='/sum/1,2,3,4,5'>Sum</a><a href='/tinh_toan?a=10&b=5&op=add'>Tính toán</a>"
@app.route("/gioi_thieu")

def gioi_thieu():
    return "Xin chào, đây là trang giới thiệu"

@app.route("/user/<username>")
def user_profile(username):
    return f"Xin chào, {username}!"

@app.route("/square/<x>")
def square(x):
    return f"{x}^2 = {x**2}"

@app.route("/square2/<x>")
def square2(x):
    return f"{float(x)}^2 = {float(x)}**2"

@app.route("/sum/<strs>")
def tong(strs):
    #1, 2, 3 = 6
    numbers = strs.split(",")
    total = sum(float(num) for num in numbers)
    return f"Tổng của {strs} là: {total}"

@app.route("/tinh_toan")
def tinh_toan():
    a = req.args.get("a")
    b = req.args.get("b")
    op = req.args.get("op")
    if op == "add":
        return f"Tổng của a và b là: {a} + {b} = {float(a) + float(b)}"
    elif op == "sub":
        return f"Hiệu của a và b là: {a} - {b} = {float(a) - float(b)}"
    else:
        return f"Vui lòng truyền đủ tham số"

if __name__ == "__main__":
    app.run(debug=True)