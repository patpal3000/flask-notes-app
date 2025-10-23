from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy #task 16\
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db' #task16
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model): #task 19
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    notes = db.relationship('Note', backref='owner', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
#----------------------------------------------------------------
# task 1
#----------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

#----------------------------------------------------------------
#task 2
#----------------------------------------------------------------
@app.route("/greet/<name>")
def greet(name):
    return render_template("greet.html", user=name)

#----------------------------------------------------------------
#task 3
#----------------------------------------------------------------
@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["username"]
    return render_template("thanks.html", name=name)

#----------------------------------------------------------------
#task 4
#----------------------------------------------------------------
@app.route("/about")
def about():
    return render_template("about.html")

#----------------------------------------------------------------
#task 6
#----------------------------------------------------------------
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        message = request.form["message"]
        return render_template("feedback.html", respone=message)
    return render_template("feedback.html", respone=None)

#----------------------------------------------------------------
#task 7 NOTES
#----------------------------------------------------------------
@app.route("/notes", methods=["GET", "POST"])
def notes_page():
    #task 21 user logic
    if "user_id" not in session:
        flash("⚠️ Please log in first.")
        return redirect("/login")
    
    user_id = session["user_id"]
    
    # add new note
    if request.method == "POST":
        note = request.form["note"]
        if note.strip():
            new_note = Note(text=note, user_id=user_id)
            db.session.add(new_note)
            db.session.commit()
            flash("✅ Note added successfully!")

    # pagination setup
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "").strip().lower()

    # base query for this user
    base_query = Note.query.filter_by(user_id=user_id)

    # optional search
    if query:
        base_query = base_query.filter(Note.text.ilike(f"%{query}%"))

    # paginate: 5 notes per page
    pagination = base_query.order_by(Note.id.desc()).paginate(page=page, per_page=5)
    notes = pagination.items

    return render_template("notes.html", notes=notes, pagination=pagination, query=query)

@app.route("/delete/<int:id>")
def delete(id):
    note = Note.query.get_or_404(id)

    if note.user_id != session.get("user_id"):
        flash("❌ Not allowed")
        return redirect("/notes")
    
    db.session.delete(note)
    db.session.commit()
    flash("🗑️ Note delete!") #task 14
    return redirect("/notes")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.text = request.form["note"]
        if note.user_id != session.get("user_id"):
            flash("❌ Not allowed")
            return redirect("/notes")
        db.session.commit()
        flash("✏️ Notes updated")
        return redirect("/notes")
    return render_template("edit.html", note=note.text)

#----------------------------------------------------------------
#task 20 user login route
#----------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("❌ Username already taken")
            return redirect("/register")
        
        if not username.strip() or len(password) < 4:
            flash("❌ Provide a username and password (min 4 chars).")
            return redirect("/register")
        
        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("✅ Registered successfully!")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("🔓 Logged in!")
            return redirect("/notes")
        flash("❌ Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("👋 Logged out.")
    return redirect("/")

@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("⚠️ Please log in first.")
        return redirect("/login")
    
    user = User.query.get(session["user_id"])
    note_count = Note.query.filter_by(user_id=user.id).count()
    return render_template("profile.html", user=user, note_count=note_count)

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        flash("⚠️ Please log in first.")
        return redirect("/login")
    
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        old = request.form["old_password"]
        new = request.form["new_password"]

        if not check_password_hash(user.password, old):
            flash("❌ Old password incorrect.")
        elif len(new) < 4:
            flash("⚠️ New password too short (min 4 chars).")
        else:
            user.password = generate_password_hash(new)
            db.session.commit()
            flash("🔒 Password updated successfully!")
            return redirect("/profile")
    
    return render_template("change_password.html")

@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        flash("⚠️ Please log in first.")
        return redirect("/login")
    
    user = User.query.get(session["user_id"])

    # Delete all note first
    Note.query.filter_by(user_id=user.id).delete()

    # Delete user
    db.session.delete(user)
    db.session.commit()

    session.pop("user_id", None)
    flash("🗑️ Account deleted permanently.")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

