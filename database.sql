CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    name varchar(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS url_checks (
    id SERIAL PRIMARY KEY,
    url_id SERIAL REFERENCES urls(id),
    status_code INT,
    h1 varchar(255),
    title varchar(255),
    description varchar(1023),
    created_at TIMESTAMP
);
