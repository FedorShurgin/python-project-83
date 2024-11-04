from flask import Flask
from dotenv import load_dotenv
import os
from jinja2 import Environment, FileSystemLoader

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


file_loader = FileSystemLoader('page_analyzer') #загрузчик
env = Environment(loader=file_loader) #окружение

tm_index = env.get_template('index.html')
tm_index  .render()