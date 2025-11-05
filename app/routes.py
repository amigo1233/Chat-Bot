from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import db, User, RequestLog
from app.plugins.groq_plugin import ask_groq

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    user = User.query.get(session["user_id"])
    return render_template("index.html", username=user.username, user_id=user.user_id)


@main_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    user_msg = (data.get("message") or "").strip()
    if not user_msg:
        return jsonify({"reply": "Напиши щось 🙂"})

    reply = ask_groq(user_msg)

    try:
        user = User.query.get(session.get("user_id"))
        db.session.add(RequestLog(user_id=user.user_id, request_text=user_msg, response_text=reply))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("DB LOG ERROR:", e)

    return jsonify({"reply": reply})


@main_bp.route("/api/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"ok": True})


@main_bp.route("/history")
def history():
    rows = RequestLog.query.order_by(RequestLog.created_at.desc()).limit(20).all()
    html = "<h2>Останні 20 звернень</h2><ol>"
    for r in rows:
        html += f"<li>#{r.request_id}: {r.request_text[:200]} → {r.response_text[:200]}</li>"
    html += "</ol>"
    return html


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not username or not email or not password:
            return render_template("register.html", error="Заповни всі поля")

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Такий логін вже існує")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.user_id
        return redirect(url_for("main.home"))

    return render_template("register.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return render_template("login.html", error="Невірний логін або пароль")

        session["user_id"] = user.user_id
        return redirect(url_for("main.home"))

    return render_template("login.html")


@main_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("main.login"))
