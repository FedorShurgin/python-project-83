CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    name varchar(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);
