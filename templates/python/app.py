from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Native Python target. bench wraps this; no Dockerfile needed.\n"

if __name__ == "__main__":
    # bench forces the bind host to 0.0.0.0; keep your own port here.
    app.run(host="0.0.0.0", port=8000)
