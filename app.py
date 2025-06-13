from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, world! My name is Shaun Owen. COP 4504 - 1635 - 0650"
