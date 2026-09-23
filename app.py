from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def home():
   a = 5
   b = 7
   # return "Xin chao";
   return render_template("math.html", a = a, b = b, cong = a +b, hieu = a - b)
if __name__ == "__main__":
    app.run(debug=True)
