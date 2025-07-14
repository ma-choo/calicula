"""
app.py - flask rest api with static frontend

local usage:
get:
curl http://localhost:5000/subcalendars

post:
curl -X POST http://localhost:5000/subcalendars \
     -H "Content-Type: application/json" \
     -d '{"name": "<date>", "assignments": []}'

azure app service deployment environment variables:
CALICULA_STORAGE_BACKEND -> azure
AZURE_CONNECTION_STRING
AZURE_CONTAINER
"""

from flask import Flask, jsonify, request, send_from_directory
from storage import get_backend
from subcalendar import Subcalendar

app = Flask(__name__, static_folder="static")
storage = get_backend()

@app.route("/subcalendars", methods=["GET"])
def get():
    subcals = storage.read_all()
    return jsonify([sc.to_dict() for sc in subcals])

@app.route("/subcalendars", methods=["POST"])
def post():
    sc = Subcalendar.from_dict(request.json)
    storage.write(sc)
    return jsonify({"status": "ok"}), 201

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
