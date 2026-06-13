DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS announcements;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE announcements (
    id INTEGER PRIMARY KEY,
    title TEXT,
    place TEXT,
    gametime TEXT,
    players INTEGER,
    description TEXT,
    userid INTEGER REFERENCES users
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE announcement_categories (
    announcement_id INTEGER REFERENCES announcements,
    category_id INTEGER REFERENCES categories,
    PRIMARY KEY (announcement_id, category_id)
);
