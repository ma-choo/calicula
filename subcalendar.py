# subcalendar.py - define assignment and subcalendar classes

import os
from typing import List
from datetime import datetime

SUBCAL_DIR = "./subcalendars"

class Assignment:
    def __init__(self, name: str, date: str, completed: bool):
        self.name = name
        self.completed = completed
        self.date = datetime.strptime(date, "%m%d%Y").date()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year

    def toggle_completion(self):
        self.completed = not self.completed

    def __repr__(self):
        return f"Assignment  name: '{self.name}'  date: {self.date.strftime('%m/%d/%Y')}  completeted: {self.completed}"

class Subcalendar:
    def __init__(self, name: str):
        self.name = name
        self.assignments: List[Assignment] = []
        self.hidden = False
        self.color = 1  # default color pair index

    # TODO: change this to insert instead of append so that each assignment is ordered by date. refactoring to DDMMYYYY might make this easier
    def add_assignment(self, assignment: Assignment):
        self.assignments.append(assignment)

    def toggle_hidden(self):
        self.hidden = not self.hidden

    def write(self):
        filename = os.path.join(SUBCAL_DIR, self.name)
        with open(filename, "w") as file:
            file.write(f"{self.color}\n")
            for a in self.assignments:
                file.write(f"{a.name},{a.month:02d}{a.day:02d}{a.year},{int(a.completed)}\n")

    @classmethod
    def read_all(cls) -> List["Subcalendar"]:
        subcalendars = []
        if not os.path.exists(SUBCAL_DIR):
            os.makedirs(SUBCAL_DIR)
        for filename in os.listdir(SUBCAL_DIR):
            subcalendar = cls(filename)
            filepath = os.path.join(SUBCAL_DIR, filename)
            with open(filepath, "r") as file:
                try:
                    line = file.readline()
                    subcalendar.color = int(line.strip())
                    for line in file:
                        parts = line.strip().split(",")
                        if len(parts) == 3:
                            name = parts[0]
                            date = parts[1]
                            completed = int(parts[2])
                            assignment = Assignment(name, date, completed)
                            subcalendar.add_assignment(assignment)
                except Exception as e:
                    # Handle corrupt files or errors gracefully
                    print(f"Error reading {filename}: {e}")
            subcalendars.append(subcalendar)
        return subcalendars

    def __repr__(self):
        return f"Subcalendar  name: '{self.name}'  color: {self.color}  assignments: {len(self.assignments)}  hidden: {self.hidden}"