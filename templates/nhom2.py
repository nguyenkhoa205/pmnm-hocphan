from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def home():
   # return "Xin chao";
   return render_template("math.html")
if __name__ == "__main__":
    app.run(debug=True)
