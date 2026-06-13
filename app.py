from flask import Flask, abort, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import secrets

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "userid" not in session:
        abort(403)


@app.route("/")
def index():
    sql = """
        SELECT A.id, A.title, A.place, A.gametime, A.players, A.description,
               U.username
        FROM announcements A
        JOIN users U ON A.userid = U.id
        ORDER BY A.id DESC
    """
    announcements = db.query(sql)
    return render_template("index.html", announcements=announcements)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "Error: passwords do not match"

    passwordhash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, passwordhash])
    except Exception:
        return "Error: username is already taken"

    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if len(result) == 0:
        return "Error: invalid username or password"

    user = result[0]
    passwordhash = user["password_hash"]

    if not check_password_hash(passwordhash, password):
        return "Error: invalid username or password"

    session["userid"] = user["id"]
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)

    return redirect("/")


@app.route("/logout")
def logout():
    if "userid" in session:
        del session["userid"]
    if "username" in session:
        del session["username"]
    if "csrf_token" in session:
        del session["csrf_token"]
    return redirect("/")


@app.route("/user/<int:user_id>")
def user_page(user_id):
    sql_user = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql_user, [user_id])
    if len(result) == 0:
        abort(404)
    user = result[0]

    sql_ann = """
        SELECT id, title, place, gametime, players
        FROM announcements
        WHERE userid = ?
        ORDER BY id DESC
    """
    announcements = db.query(sql_ann, [user_id])

    count = len(announcements)

    return render_template(
        "user.html",
        user=user,
        announcements=announcements,
        count=count,
    )

@app.route("/announcements/new")
def new_announcement():
    require_login()

    sql = "SELECT id, name FROM categories ORDER BY name"
    categories = db.query(sql)

    return render_template("new_announcement.html", categories=categories)


@app.route("/announcements/create", methods=["POST"])
def create_announcement():
    require_login()

    title = request.form["title"]
    place = request.form["place"]
    gametime = request.form["gametime"]
    players = request.form["players"]
    description = request.form["description"]
    userid = session["userid"]

    sql = """
        INSERT INTO announcements (title, place, gametime, players, description, userid)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    db.execute(sql, [title, place, gametime, players, description, userid])

    announcement_id = db.last_insert_id()

    category_ids = request.form.getlist("category_ids")
    for cid in category_ids:
        sql = """
            INSERT INTO announcement_categories (announcement_id, category_id)
            VALUES (?, ?)
        """
        db.execute(sql, [announcement_id, int(cid)])

    return redirect("/")


@app.route("/announcements/<int:announcement_id>")
def show_announcement(announcement_id):
    sql = """
        SELECT A.id, A.title, A.place, A.gametime, A.players, A.description,
               A.userid, U.username
        FROM announcements A
        JOIN users U ON A.userid = U.id
        WHERE A.id = ?
    """
    result = db.query(sql, [announcement_id])
    if len(result) == 0:
        abort(404)

    announcement = result[0]
    return render_template("announcement.html", announcement=announcement)


@app.route("/announcements/<int:announcement_id>/edit")
def edit_announcement(announcement_id):
    require_login()

    sql = "SELECT * FROM announcements WHERE id = ?"
    result = db.query(sql, [announcement_id])
    if len(result) == 0:
        abort(404)

    announcement = result[0]
    if announcement["userid"] != session["userid"]:
        abort(403)

    return render_template("edit_announcement.html", announcement=announcement)


@app.route("/announcements/<int:announcement_id>/update", methods=["POST"])
def update_announcement(announcement_id):
    require_login()

    sql = "SELECT userid FROM announcements WHERE id = ?"
    result = db.query(sql, [announcement_id])
    if len(result) == 0:
        abort(404)
    if result[0]["userid"] != session["userid"]:
        abort(403)

    title = request.form["title"]
    place = request.form["place"]
    gametime = request.form["gametime"]
    players = request.form["players"]
    description = request.form["description"]

    sql = """
        UPDATE announcements
        SET title = ?, place = ?, gametime = ?, players = ?, description = ?
        WHERE id = ?
    """
    db.execute(sql, [title, place, gametime, players, description, announcement_id])
    return redirect(f"/announcements/{announcement_id}")


@app.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
def delete_announcement(announcement_id):
    require_login()

    sql = "SELECT userid FROM announcements WHERE id = ?"
    result = db.query(sql, [announcement_id])
    if len(result) == 0:
        abort(404)
    if result[0]["userid"] != session["userid"]:
        abort(403)

    db.execute("DELETE FROM announcements WHERE id = ?", [announcement_id])
    return redirect("/")


@app.route("/search")
def search():
    query_text = request.args.get("q", "")
    like = f"%{query_text}%"

    sql = """
        SELECT A.id, A.title, A.place, A.gametime, A.players, A.description,
               U.username
        FROM announcements A
        JOIN users U ON A.userid = U.id
        WHERE A.title LIKE ? OR A.place LIKE ? OR A.description LIKE ?
        ORDER BY A.id DESC
    """
    announcements = db.query(sql, [like, like, like])
    return render_template(
        "index.html",
        announcements=announcements,
        search=query_text
    )
