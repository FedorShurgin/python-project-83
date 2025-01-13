from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
from page_analyzer.urls import parse, validate_url
import requests
from page_analyzer.parser import parse_html
from page_analyzer.repository import UrlsRepository


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
repo = UrlsRepository(DATABASE_URL)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls")
def urls_get():
    urls = repo.get_urls_list()
    return render_template("urls.html", urls=urls)


@app.route("/urls", methods=['POST'])
def urls_post():
    url = request.form.get('url')

    error_url = validate_url(url)

    if error_url:
        flash(error_url, 'alert-danger')
        return render_template('index.html'), 422

    pars_url = parse(url)

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
    _ = repo.add_check(id, response.status_code, parse_html(response.text))
    flash('Страница успешно проверена', 'alert-success')
    return redirect(url_for('url_show', id=id))


if __name__ == "__main__":
    app.run(debug=True)
