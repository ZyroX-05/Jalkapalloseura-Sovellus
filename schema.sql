DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS signups;
DROP TABLE IF EXISTS comments;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE announcements (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    place TEXT NOT NULL,
    gametime TEXT NOT NULL,
    players INTEGER NOT NULL,
    description TEXT NOT NULL,
    userid INTEGER NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (userid) REFERENCES users(id)
);

CREATE TABLE signups (
    id INTEGER PRIMARY KEY,
    announcement_id INTEGER NOT NULL,
    userid INTEGER NOT NULL,
    FOREIGN KEY (announcement_id) REFERENCES announcements(id),
    FOREIGN KEY (userid) REFERENCES users(id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    announcement_id INTEGER NOT NULL,
    userid INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (announcement_id) REFERENCES announcements(id),
    FOREIGN KEY (userid) REFERENCES users(id)
);
