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

