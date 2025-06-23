# subcalendar.py

class Assignment:
    def __init__(self, name: str, day: int, month: int, year: int):
        self.name = name
        self.day = day
        self.month = month
        self.year = year

class Calendar:
    def __init__(self, name: str):
        self.name = name
        self.assignments: List[Assignment] = []
        self.hidden = False

    def add_event(self, assignment: Assignment):
        self.assignments.append(assignment)
