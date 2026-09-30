from flask import Flask
app = Flask(__name__)
app.json.ensure_ascii = False # JSON hiển thị tiếng Việt có dấu thay vì \uXXXX

@app.route("/")
def index():
return "<h1>MiniBlog</h1>"