# subcalendar.py

class Assignment:
  def __init__(self, name: str, date: str, completed: bool):
    self.name = name
    self.completed = completed
    self.date = date

  def toggle_completion(self):
    self.completed = not self.completed

# create a constructor that takes a filename string

class Subcalendar:
  def __init__(self, name: str):
    self.name = name
    self.color = 0
    self.assignments = []
    self.hidden = False

  def add_assignment(self, assignment: Assignment):
    self.assignments.append(assignment)

  def show(self):
    print(self.name, self.color, self.hidden)
    for assignment in self.assignments:
      print(assignment.name, assignment.date, assignment.completed)
