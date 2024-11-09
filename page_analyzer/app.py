from flask import Flask, render_template
from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


list_urls = [{'id': 'id', 'name': 'name_url', 'last_check': 'data', 'response_code': 'code'},
            {'id': 'id', 'name': 'name_url', 'last_check': 'data', 'response_code': 'code'},
            {'id': 'id', 'name': 'name_url', 'last_check': 'data', 'response_code': 'code'}
        ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls")
def urls_get():
    return render_template('urls.html', list_urls=list_urls)


if __name__ == "__main__":
    app.run(debug=True)
