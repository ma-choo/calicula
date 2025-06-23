# app.py

from flask import Flask
from subcalendar import Assignment, Subcalendar

app = Flask(__name__)

@app.route('/')
def main():
    subcalendars = []
    subcalendar = Subcalendar("COP4504")
    subcalendars.append(subcalendar)


    with open("subcalendars/cop4504", "r") as file:
        # read first line as calendar color
        line = file.readline()
        subcalendars[0].color = int(line.strip())

        # read and parse the remaining lines as assignments
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 3:
                name = str(parts[0])
                date = str(parts[1])
                completed = int(parts[2])
                assignment = Assignment(name, date, completed)
                subcalendars[0].add_assignment(assignment)

    subcalendars[0].show()
    
    return "Hello, world! My name is Shaun Owen. COP 4504 - 1635 - 0650"
