from flask import Flask

app = Flask(__name__)

memory = []

@app.route("/")
def home():
    while True:
        memory.append("A" * 1024 * 1024)

    return "Hello"

@app.route("/health")
def health():
    return "OK"

app.run(host="0.0.0.0", port=5000)