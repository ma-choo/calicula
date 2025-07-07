import os
from typing import List
from datetime import datetime

class Assignment:
    def __init__(self, name: str, date: str, completed: bool):
        self.name = name
        self.completed = completed
        self.date = datetime.strptime(date, "%Y%m%d").date()
        self.month = self.date.month
        self.day = self.date.day
        self.year = self.date.year

    def rename(self, name: str):
        self.name = name

    def toggle_completion(self):
        self.completed = not self.completed

    def __repr__(self):
        return f"Assignment  name: '{self.name}'  date: {self.date.strftime('%m/%d/%Y')}  completed: {self.completed}"

    def to_dict(self):
        return {
            "name": self.name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            year=data["year"],
            month=data["month"],
            day=data["day"],
            completed=data.get("completed", False)
        )

class Subcalendar:
    def __init__(self, name: str, color=1):
        self.name = name
        self.assignments: List[Assignment] = []
        self.hidden = False
        self.color = color

    def rename(self, name: str):
        self.name = name

    def insert_assignment(self, assignment: Assignment):
        for i, existing in enumerate(self.assignments):
            if assignment.date < existing.date:
                self.assignments.insert(i, assignment)
                return
        self.assignments.append(assignment)

    def toggle_hidden(self):
        self.hidden = not self.hidden

    def change_color (self, color):
        self.color = color

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "hidden": self.hidden,
            "assignments": [a.to_dict() for a in self.assignments]
        }

    @classmethod
    def from_dict(cls, data):
        subcal = cls(data["name"], data.get("color", 1))
        subcal.hidden = data.get("hidden", False)
        subcal.assignments = [Assignment.from_dict(a) for a in data.get("assignments", [])]
        return subcal

    # ---- LOCAL FILE I/O ----
    @classmethod
    def read_all_local(cls, directory: str) -> List["Subcalendar"]:
        subcalendars = []
        if not os.path.exists(directory):
            os.makedirs(directory)
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue
            with open(filepath, "r") as file:
                subcalendar = cls._read_from_file(filename, file)
                subcalendars.append(subcalendar)
        return subcalendars

    @classmethod
    def _read_from_file(cls, name, file):
        subcalendar = cls(name)
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
                    subcalendar.insert_assignment(assignment)
        except Exception as e:
            print(f"Error reading {name}: {e}")
        return subcalendar

    def write_local(self, directory: str):
        filename = os.path.join(directory, self.name)
        with open(filename, "w") as file:
            file.write(f"{self.color}\n")
            for a in self.assignments:
                file.write(f"{a.name},{a.date.strftime('%Y%m%d')},{int(a.completed)}\n")

    # ---- BLOB STORAGE I/O ----
    @classmethod
    def from_blob(cls, name: str, data: str) -> "Subcalendar":
        from io import StringIO
        file = StringIO(data)
        return cls._read_from_file(name, file)

    def to_blob(self) -> str:
        lines = [f"{self.color}"]
        for a in self.assignments:
            lines.append(f"{a.name},{a.date.strftime('%Y%m%d')},{int(a.completed)}")
        return "\n".join(lines)

    def __repr__(self):
        return f"Subcalendar  name: '{self.name}'  color: {self.color}  assignments: {len(self.assignments)}  hidden: {self.hidden}"
