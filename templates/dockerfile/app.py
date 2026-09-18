from flask import Flask
app = Flask(__name__)

FLAG = "f13{change_me}"

@app.route("/")
def index():
    return "Replace me with an intentionally vulnerable app.\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
