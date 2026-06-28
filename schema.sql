DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS announcement_categories;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS signups;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE announcements (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    place TEXT NOT NULL,
    gametime TEXT NOT NULL,
    players INTEGER NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    userid INTEGER NOT NULL REFERENCES users
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE announcement_categories (
    announcement_id INTEGER REFERENCES announcements ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories,
    PRIMARY KEY (announcement_id, category_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users,
    announcement_id INTEGER NOT NULL REFERENCES announcements ON DELETE CASCADE
);

CREATE TABLE signups (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users ON DELETE CASCADE,
    announcement_id INTEGER NOT NULL REFERENCES announcements ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    UNIQUE (user_id, announcement_id)
);
