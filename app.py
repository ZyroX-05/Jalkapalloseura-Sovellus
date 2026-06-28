from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "userid" not in session:
        return redirect("/login")
    return None


def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


def check_csrf():
    token = session.get("csrf_token")
    form_token = request.form.get("csrf_token")
    if not token or token != form_token:
        return redirect("/")


@app.before_request
def before_request():
    set_csrf_token()


@app.route("/")
def index():
    need_login = require_login()
    if need_login:
        return need_login

    announcements = db.query(
        """
        SELECT id, title, place, gametime, players, category
        FROM announcements
        ORDER BY gametime
        """
    )
    return render_template("index.html", announcements=announcements)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "GET":
        return render_template("login.html", error=error)

    username = request.form.get("username")
    password = request.form.get("password")

    user_rows = db.query(
        "SELECT id, password_hash FROM users WHERE username = ?", [username]
    )
    if not user_rows:
        error = "Username not found."
        return render_template("login.html", error=error)

    user = user_rows[0]
    if not check_password_hash(user["password_hash"], password):
        error = "Incorrect password."
        return render_template("login.html", error=error)

    session["userid"] = user["id"]
    session["username"] = username
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "GET":
        return render_template("register.html", error=error)

    username = request.form.get("username")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if not username or not password1 or not password2:
        error = "Please fill in all fields."
        return render_template("register.html", error=error)

    if password1 != password2:
        error = "Passwords do not match. Try again."
        return render_template("register.html", error=error)

    existing = db.query(
        "SELECT id FROM users WHERE username = ?", [username]
    )
    if existing:
        error = "Username already taken."
        return render_template("register.html", error=error)

    password_hash = generate_password_hash(password1)
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        [username, password_hash],
    )
    return render_template("register_success.html", username=username)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/announcements/new")
def new_announcement():
    need_login = require_login()
    if need_login:
        return need_login

    return render_template("new_announcement.html")


@app.route("/announcements/create", methods=["POST"])
def create_announcement():
    need_login = require_login()
    if need_login:
        return need_login

    if check_csrf():
        return check_csrf()

    title = request.form.get("title")
    place = request.form.get("place")
    gametime = request.form.get("gametime")
    players = request.form.get("players")
    description = request.form.get("description")
    category = request.form.get("category")

    error = None

    if not title or not place or not gametime or not players or not description or not category:
        error = "All fields are required."
        return render_template("new_announcement.html", error=error)

    try:
        players_int = int(players)
    except ValueError:
        error = "Players must be a number."
        return render_template("new_announcement.html", error=error)

    if players_int < 1:
        error = "Players must be at least 1."
        return render_template("new_announcement.html", error=error)

    if players_int > 40:
        error = "Events with more than 40 players are not allowed."
        return render_template("new_announcement.html", error=error)

    if len(description) > 500:
        error = "Description must be at most 500 characters."
        return render_template("new_announcement.html", error=error)

    db.execute(
        """
        INSERT INTO announcements (title, place, gametime, players, description, userid, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [title, place, gametime, players_int, description, session["userid"], category],
    )
    announcement_id = db.last_insert_id()
    return redirect(f"/announcements/{announcement_id}")


@app.route("/announcements/<int:announcement_id>")
def show_announcement(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    announcement_rows = db.query(
        """
        SELECT a.id, a.title, a.place, a.gametime, a.players,
               a.description, a.userid, a.category, u.username
        FROM announcements a
        JOIN users u ON a.userid = u.id
        WHERE a.id = ?
        """,
        [announcement_id],
    )
    if not announcement_rows:
        return redirect("/")

    announcement = announcement_rows[0]

    signup_users = db.query(
        """
        SELECT u.username
        FROM signups s
        JOIN users u ON s.userid = u.id
        WHERE s.announcement_id = ?
        """,
        [announcement_id],
    )
    signup_count = len(signup_users)

    user_signed_up = False
    if session.get("userid"):
        signed = db.query(
            """
            SELECT 1
            FROM signups
            WHERE announcement_id = ? AND userid = ?
            """,
            [announcement_id, session["userid"]],
        )
        user_signed_up = bool(signed)

    comments = db.query(
        """
        SELECT c.content, c.created_at, u.username
        FROM comments c
        JOIN users u ON c.userid = u.id
        WHERE c.announcement_id = ?
        ORDER BY c.created_at DESC
        """,
        [announcement_id],
    )

    return render_template(
        "announcement.html",
        announcement=announcement,
        signup_users=signup_users,
        signup_count=signup_count,
        user_signed_up=user_signed_up,
        comments=comments,
    )


@app.route("/announcements/<int:announcement_id>/signup", methods=["POST"])
def signup(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    if check_csrf():
        return check_csrf()

    existing = db.query(
        """
        SELECT 1
        FROM signups
        WHERE announcement_id = ? AND userid = ?
        """,
        [announcement_id, session["userid"]],
    )
    if not existing:
        db.execute(
            """
            INSERT INTO signups (announcement_id, userid)
            VALUES (?, ?)
            """,
            [announcement_id, session["userid"]],
        )

    return redirect(f"/announcements/{announcement_id}")

@app.route("/announcements/<int:announcement_id>/comments", methods=["POST"])
def add_comment(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    if check_csrf():
        return check_csrf()

    content = request.form.get("content")

    if not content:
        return redirect(f"/announcements/{announcement_id}")

    db.execute(
        """
        INSERT INTO comments (announcement_id, userid, content, created_at)
        VALUES (?, ?, ?, datetime('now'))
        """,
        [announcement_id, session["userid"], content],
    )

    return redirect(f"/announcements/{announcement_id}")


@app.route("/announcements/<int:announcement_id>/cancel", methods=["POST"])
def cancel_signup(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    if check_csrf():
        return check_csrf()

    db.execute(
        """
        DELETE FROM signups
        WHERE announcement_id = ? AND userid = ?
        """,
        [announcement_id, session["userid"]],
    )
    return redirect(f"/announcements/{announcement_id}")


@app.route("/announcements/<int:announcement_id>/edit")
def edit_announcement(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    announcement_rows = db.query(
        """
        SELECT id, title, place, gametime, players, description, userid, category
        FROM announcements
        WHERE id = ?
        """,
        [announcement_id],
    )
    if not announcement_rows:
        return redirect("/")

    announcement = announcement_rows[0]
    if announcement["userid"] != session["userid"]:
        return redirect("/")

    return render_template("edit.html", announcement=announcement)


@app.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
def delete_announcement(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    if check_csrf():
        return check_csrf()

    announcement_rows = db.query(
        "SELECT userid FROM announcements WHERE id = ?", [announcement_id]
    )
    if not announcement_rows or announcement_rows[0]["userid"] != session["userid"]:
        return redirect("/")

    db.execute(
        "DELETE FROM signups WHERE announcement_id = ?",
        [announcement_id],
    )

    db.execute(
        "DELETE FROM comments WHERE announcement_id = ?",
        [announcement_id],
    )

    db.execute(
        "DELETE FROM announcements WHERE id = ?",
        [announcement_id],
    )

    return redirect("/")


@app.route("/announcements/<int:announcement_id>/update", methods=["POST"])
def update_announcement(announcement_id):
    need_login = require_login()
    if need_login:
        return need_login

    if check_csrf():
        return check_csrf()

    announcement_rows = db.query(
        "SELECT userid FROM announcements WHERE id = ?", [announcement_id]
    )
    if not announcement_rows or announcement_rows[0]["userid"] != session["userid"]:
        return redirect("/")

    title = request.form.get("title")
    place = request.form.get("place")
    gametime = request.form.get("gametime")
    players = request.form.get("players")
    description = request.form.get("description")
    category = request.form.get("category")

    error = None
    players_int = None

    if not title or not place or not gametime or not players or not description or not category:
        error = "All fields are required."
    else:
        try:
            players_int = int(players)
        except ValueError:
            error = "Players must be a number."
        else:
            if players_int < 1:
                error = "Players must be at least 1."
            elif players_int > 40:
                error = "Events with more than 40 players are not allowed."
            elif len(description) > 500:
                error = "Description must be at most 500 characters."

    if error:
        announcement = {
            "id": announcement_id,
            "title": title,
            "place": place,
            "gametime": gametime,
            "players": players,
            "description": description,
            "userid": session["userid"],
            "category": category,
        }
        return render_template("edit.html", announcement=announcement, error=error)

    db.execute(
        """
        UPDATE announcements
        SET title = ?, place = ?, gametime = ?, players = ?, description = ?, category = ?
        WHERE id = ?
        """,
        [title, place, gametime, players_int, description, category, announcement_id],
    )
    return redirect(f"/announcements/{announcement_id}")


@app.route("/search", methods=["GET", "POST"])
def search():
    need_login = require_login()
    if need_login:
        return need_login

    if request.method == "GET":
        return render_template("search.html")

    query = request.form.get("query")
    announcements = db.query(
        """
        SELECT id, title, place, gametime, players, category
        FROM announcements
        WHERE title LIKE ? OR gametime LIKE ?
        ORDER BY gametime
        """,
        [f"%{query}%", f"%{query}%"],
    )
    return render_template("search.html", announcements=announcements, query=query)


@app.route("/user/<int:userid>")
def user_page(userid):
    need_login = require_login()
    if need_login:
        return need_login

    user_rows = db.query(
        "SELECT id, username FROM users WHERE id = ?", [userid]
    )
    if not user_rows:
        return redirect("/")

    user = user_rows[0]

    count_rows = db.query(
        "SELECT COUNT(*) AS count FROM announcements WHERE userid = ?", [userid]
    )
    count = count_rows[0]["count"]

    announcements = db.query(
        """
        SELECT id, title, place, gametime, players, category
        FROM announcements
        WHERE userid = ?
        ORDER BY gametime
        """,
        [userid],
    )

    return render_template(
        "user.html",
        user=user,
        count=count,
        announcements=announcements,
    )
