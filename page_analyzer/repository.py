from psycopg2.extras import DictCursor


class UrlsRepository:
    def __init__(self, conn):
        self.conn = conn
        
        
    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
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
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s;", (id,))
            result = cur.fetchone()
        return result


    def get_url_by_name(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s;", (name,))
            result = cur.fetchone()
        return result
    
    
    def get_checks_by_url_id(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC;", (id,))
            result = cur.fetchall()
        return result


    def get_latest_check_by_url_id(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC LIMIT 1;", (id,))
            result = cur.fetchone()
        return result
    
    
    def add_url(self, url):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, now()) RETURNING id;",
                (url,)
            )
            result = cur.fetchone()
        self.conn.commit()
        return result


    def add_check(self, url_id, status_code,h1, title, description):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s, %s, %s, now()) RETURNING id;",
                (url_id, status_code, h1, title, description)
            )
            result = cur.fetchone()
        self.conn.commit()
        return result
