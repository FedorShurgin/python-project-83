from psycopg2.extras import DictCursor
import psycopg2


class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_name)
        self.cur = self.conn.cursor(cursor_factory=DictCursor)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


class UrlsRepository:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_content(self):
        with DatabaseConnection(self.db_name) as cur:
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

    def get_url_by_id(self, id):
        with DatabaseConnection(self.db_name) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s;", (id,))
            result = cur.fetchone()
        return result

    def get_url_by_name(self, name):
        with DatabaseConnection(self.db_name) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s;", (name,))
            result = cur.fetchone()
        return result

    def get_checks_by_url_id(self, id):
        with DatabaseConnection(self.db_name) as cur:
            cur.execute("""
                        SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY created_at DESC;
                        """,
                        (id,)
                        )
            result = cur.fetchall()
        return result

    def get_latest_check_by_url_id(self, id):
        with DatabaseConnection(self.db_name) as cur:
            cur.execute("""
                        SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY created_at DESC LIMIT 1;
                        """,
                        (id,)
                        )
            result = cur.fetchone()
        return result

    def add_url(self, url):
        with DatabaseConnection(self.db_name) as cur:
            cur.execute("""
                        INSERT INTO urls (name, created_at)
                        VALUES (%s, now())
                        RETURNING id;
                        """,
                        (url,)
                        )
            result = cur.fetchone()
        return result

    def add_check(self, url_id, status_code, html):
        with DatabaseConnection(self.db_name) as cur:
            cur.execute("""
                        INSERT INTO url_checks (
                                                url_id,
                                                status_code,
                                                h1,
                                                title,
                                                description,
                                                created_at
                                                )
                        VALUES (%s, %s, %s, %s, %s, now())
                        RETURNING id;
                        """,
                        (
                            url_id,
                            status_code,
                            html['h1'],
                            html['title'],
                            html['description']
                            )
                        )
            result = cur.fetchone()
        return result
