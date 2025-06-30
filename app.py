# app.py

from flask import Flask, Response
from subcalendar import Subcalendar

app = Flask(__name__)

@app.route("/")
def debug_calendars():
    subcalendars = Subcalendar.read_all()
    output = "\n".join(repr(cal) for cal in subcalendars)
    return Response(output, mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
