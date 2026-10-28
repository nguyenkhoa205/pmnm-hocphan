from flask import Flask, render_template, request

app = Flask(__name__)


def validate_score(val_str):
    """Hàm kiểm tra điểm dùng chung cho cả 3 ô (CC, GK, CK)."""
    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."

    clean_str = val_str.strip().replace(",", ".")
    try:
        val = float(clean_str)
    except ValueError:
        return None, "Vui lòng nhập một số."

    if val < 0 or val > 10:
        return None, "Điểm phải từ 0 đến 10."

    return val, None


def get_letter_grade(score, ck_val):
    """Quy đổi điểm chữ và kiểm tra điểm liệt cuối kỳ (< 1)."""
    if ck_val < 1.0:
        return "F (điểm thi dưới 1)"

    if score >= 8.5:
        return "A"
    elif score >= 7.0:
        return "B"
    elif score >= 5.5:
        return "C"
    elif score >= 4.0:
        return "D"
    else:
        return "F"


@app.route("/", methods=["GET", "POST"])
def grade():
    cc_str = ""
    gk_str = ""
    ck_str = ""
    result = None
    errors = {}

    if request.method == "POST":
        cc_str = request.form.get("cc", "")
        gk_str = request.form.get("gk", "")
        ck_str = request.form.get("ck", "")

        cc_val, err_cc = validate_score(cc_str)
        if err_cc:
            errors["cc"] = err_cc

        gk_val, err_gk = validate_score(gk_str)
        if err_gk:
            errors["gk"] = err_gk

        ck_val, err_ck = validate_score(ck_str)
        if err_ck:
            errors["ck"] = err_ck

        if not errors:
            final_score = round(0.1 * cc_val + 0.3 * gk_val + 0.6 * ck_val, 1)
            letter = get_letter_grade(final_score, ck_val)
            result = f"{final_score} - {letter}"

    return render_template(
        "index.html",
        cc=cc_str,
        gk=gk_str,
        ck=ck_str,
        result=result,
        errors=errors,
    )


if __name__ == "__main__":
    app.run(debug=True)