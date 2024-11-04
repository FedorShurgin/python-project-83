from flask import Flask
from dotenv import load_dotenv
import os
from jinja2 import Environment, FileSystemLoader

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)

'''
file_loader = FileSystemLoader('page_analyzer') #загрузчик
env = Environment(loader=file_loader) #окружение

tm_index = env.get_template('index.html')
tm_index.render()
'''