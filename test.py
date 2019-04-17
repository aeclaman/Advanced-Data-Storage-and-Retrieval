from flask import Flask, jsonify

app=Flask(__name__)

@app.route("/")
def home():
    return "try sending a request to /<name>"

@app.route("/<name>")
def nameroute(name):
    return jsonify({
        "message":f"Hello, {name}"
    })


if __name__ == "__main__":
    app.run(debug=True)