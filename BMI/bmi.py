from flask import Flask, render_template, request

app = Flask(__name__)


def validate_height(val_str):
    """Kiểm tra chiều cao (cm): khoảng 50 - 250 cm."""
    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."

    clean_str = val_str.strip().replace(",", ".")
    try:
        val = float(clean_str)
    except ValueError:
        return None, "Vui lòng nhập một số."

    if val < 50 or val > 250:
        if val < 50:
            return None, "Giá trị phải từ 50 đến 250. (nhập mét thay vì cm)"
        return None, "Giá trị phải từ 50 đến 250."

    return val, None


def validate_weight(val_str):
    """Kiểm tra cân nặng (kg): khoảng 10 - 300 kg."""
    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."

    clean_str = val_str.strip().replace(",", ".")
    try:
        val = float(clean_str)
    except ValueError:
        return None, "Vui lòng nhập một số."

    if val < 10 or val > 300:
        return None, "Giá trị phải từ 10 đến 300."

    return val, None


@app.route("/", methods=["GET", "POST"])
def calculate_bmi():
    height_str = ""
    weight_str = ""
    result = None
    errors = {}

    if request.method == "POST":
        height_str = request.form.get("height", "")
        weight_str = request.form.get("weight", "")

        # Kiểm tra ô chiều cao
        h_val, err_h = validate_height(height_str)
        if err_h:
            errors["height"] = err_h

        # Kiểm tra ô cân nặng
        w_val, err_w = validate_weight(weight_str)
        if err_w:
            errors["weight"] = err_w

        # Tính toán nếu dữ liệu hợp lệ
        if not errors:
            h_m = h_val / 100.0
            bmi_val = round(w_val / (h_m**2), 1)

            # Phân loại theo chuẩn Châu Á & gán màu sắc
            if bmi_val < 18.5:
                category = "Thiếu cân"
                color = "yellow"
            elif bmi_val < 23.0:
                category = "Bình thường"
                color = "green"
            elif bmi_val < 25.0:
                category = "Thừa cân"
                color = "yellow"
            else:
                category = "Béo phì"
                color = "red"

            # Cân nặng nên có (BMI từ 18.5 đến 22.9)
            min_w = round(18.5 * (h_m**2), 1)
            max_w = round(22.9 * (h_m**2), 1)

            result = {
                "bmi": bmi_val,
                "category": category,
                "color": color,
                "ideal_weight": f"{min_w}–{max_w} kg",
            }

    return render_template(
        "index.html",
        height=height_str,
        weight=weight_str,
        result=result,
        errors=errors,
    )


if __name__ == "__main__":
    app.run(debug=True)