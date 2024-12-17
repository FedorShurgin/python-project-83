from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from page_analyzer.parser import parse
import validators
import requests
from bs4 import BeautifulSoup
from page_analyzer.valid_length import is_valid_len
from page_analyzer.valid_tags import is_valid_tags


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


@app.route("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template("index.html", messages=messages)


@app.route("/urls")
def urls_get():
    urls = get_join_entities(conn)
    return render_template("urls.html", urls=urls)


@app.route("/urls", methods=['POST'])
def urls_post():
    url = request.form.get('url')
    
    if not is_valid_len(url):
        flash('URL превышает 255 символов', 'alert-danger')
        return redirect (url_for('index'))
    
    if not validators.url(url):
        flash('Некорректный URL', 'alert-danger')
        return redirect(url_for('index'))
    
    result = get_entity_by_name(conn,parse(url))
    if not result:
        result = add_entities(conn, parse(url))
        conn.commit()
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('url_show', id=result['id']))
    flash('Страница уже существует', 'alert-info')
    return redirect(url_for('url_show', id=result['id']))


@app.route('/urls/<int:id>')
def url_show(id):
    url = get_entity(conn, id)
    if not url:
        return render_template("url_error.html")
    checks = get_checks_by_url_id(conn, id)
    messages = get_flashed_messages(with_categories=True)
    return render_template("url_id.html", url=url, checks=checks ,messages=messages)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_post(id):
    url = get_entity(conn, id)
    try:
        response = requests.get(url['name'])
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('url_show', id=id))
    soup = BeautifulSoup(response.text, 'html.parser')
    check_id = add_check(conn, id, response.status_code, *is_valid_tags(soup))
    conn.commit()
    return redirect(url_for('url_show', id=id))


def add_entities(connection, entities):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, now()) RETURNING id;",
            (entities,)
        )
        result = cur.fetchone()
    return result


def get_entity(connection, entity_id):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s;", (entity_id,))
        result = cur.fetchone()
    return result


def get_entity_by_name(connection, name):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM urls WHERE name = %s;", (name,))
        result = cur.fetchone()
    return result


def add_check(connection, url_id, status_code,h1, title, description):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s, %s, %s, now()) RETURNING id;",
            (url_id, status_code, h1, title, description)
        )
        result = cur.fetchone()
    return result

def get_checks_by_url_id(connection, url_id):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC;", (url_id,))
        result = cur.fetchall()
    return result


def get_latest_check_by_url_id(connection, url_id):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC LIMIT 1;", (url_id,))
        result = cur.fetchone()
    return result


def get_join_entities(connection):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
                    SELECT
                        u.id,
                        u.name,
                        u.created_at,
                        uc.status_code,
                        uc.created_at as last_check_at
                    FROM urls u
                    left join url_checks uc on u.id = uc.url_id
                    and uc.created_at = (
                        select
                            max(created_at)
                        from url_checks
                        where url_id = u.id
                        )
                    order by u.created_at DESC;
                    """)
        result = cur.fetchall()
    return result


if __name__ == "__main__":
    app.run(debug=True)

#вспомнить теория работа с базой данных во фласк!
#создание собственных контекстных менеджеров!
#логика обработчиков должна быть простой
#обработчик ошибок во фласк