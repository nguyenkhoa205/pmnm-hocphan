from flask import Flask, render_template, request

app = Flask(__name__)


def parse_number(val_str):
    """Xử lý ép kiểu sang số thực, hỗ trợ nhập dấu phẩy (2,5)"""
    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."

    clean_str = val_str.strip().replace(",", ".")
    try:
        val = float(clean_str)
        return val, None
    except ValueError:
        return None, "Vui lòng nhập một số."


def format_num(val):
    """Bỏ phần thập phân nếu là số nguyên (vd: 8.0 -> 8, 3.5 -> 3.5)"""
    if val.is_integer():
        return int(val)
    return val


@app.route("/", methods=["GET", "POST"])
def calc():
    a_str = ""
    b_str = ""
    op = "+"
    result = None
    errors = {}

    if request.method == "POST":
        a_str = request.form.get("a", "")
        op = request.form.get("op", "+")
        b_str = request.form.get("b", "")

        a_val, err_a = parse_number(a_str)
        if err_a:
            errors["a"] = err_a

        b_val, err_b = parse_number(b_str)
        if err_b:
            errors["b"] = err_b

        valid_ops = ["+", "-", "*", "/"]
        if op not in valid_ops:
            errors["op"] = "Phép toán không hợp lệ."

        if not err_b and op == "/" and b_val == 0:
            errors["b"] = "Không thể chia cho 0."

        if not errors:
            if op == "+":
                res_num = a_val + b_val
            elif op == "-":
                res_num = a_val - b_val
            elif op == "*":
                res_num = a_val * b_val
            elif op == "/":
                res_num = a_val / b_val

            result = f"{format_num(a_val)} {op} {format_num(b_val)} = {format_num(res_num)}"

    return render_template(
        "index.html",
        a=a_str,
        b=b_str,
        op=op,
        result=result,
        errors=errors,
    )


if __name__ == "__main__":
    app.run(debug=True)