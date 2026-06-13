DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS announcement_categories;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS signups;


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

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT,
    created_at TEXT,
    user_id INTEGER REFERENCES users,
    announcement_id INTEGER REFERENCES announcements
);

CREATE TABLE signups (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    announcement_id INTEGER REFERENCES announcements,
    created_at TEXT,
    UNIQUE (user_id, announcement_id)
);
