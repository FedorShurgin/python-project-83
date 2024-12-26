from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
import psycopg2
from page_analyzer.parser import parse, is_valid_len
import validators
import requests
from bs4 import BeautifulSoup
from page_analyzer.tags_parsing import tags_parsing
from page_analyzer.repository import UrlsRepository


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
repo = UrlsRepository(conn)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls")
def urls_get():
    urls = repo.get_content()
    return render_template("urls.html", urls=urls)


@app.route("/urls", methods=['POST'])
def urls_post():
    url = request.form.get('url')
    pars_url = parse(url)
    
    if not is_valid_len(url):
        flash('URL превышает 255 символов', 'alert-danger')
        return redirect (url_for('index'))
    
    if not validators.url(url):
        flash('Некорректный URL', 'alert-danger')
        return redirect(url_for('index'))
    
    result = repo.get_url_by_name(pars_url)
    if not result:
        result = repo.add_url(pars_url)
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('url_show', id=result['id']))
    flash('Страница уже существует', 'alert-info')
    return redirect(url_for('url_show', id=result['id']))


@app.route('/urls/<int:id>')
def url_show(id):
    url = repo.get_url_by_id(id)
    if not url:
        return render_template("url_error.html")
    checks = repo.get_checks_by_url_id(id)
    return render_template("url_id.html", url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_post(id):
    url = repo.get_url_by_id(id)
    try:
        response = requests.get(url['name'])
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('url_show', id=id))
    soup = BeautifulSoup(response.text, 'html.parser')
    check_id = repo.add_check(id, response.status_code, *tags_parsing(soup))
    return redirect(url_for('url_show', id=id))


if __name__ == "__main__":
    app.run(debug=True)

#создание собственных контекстных менеджеров!