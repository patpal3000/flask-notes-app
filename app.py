from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy #task 16\
from werkzeug.security import generate_password_hash, check_password_hash
import json, os

app = Flask(__name__)
app.secret_key = "notme123" #task 14 - flash message
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
#task 5
#----------------------------------------------------------------
@app.route("/profile")
def profile():
    user = {
        "name": "RDH",
        "age": 25,
        "hobby": "coding"
    }
    return render_template("profile.html", user=user)

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
#task 7 create
#----------------------------------------------------------------
@app.route("/notes", methods=["GET", "POST"])
def notes_page():
    # add new note
    if request.method == "POST":
        note = request.form["note"]
        if note.strip():
            new_note = Note(text=note)
            db.session.add(new_note)
            db.session.commit()
            flash("✅ Note added successfully!") #task 14

    notes = Note.query.all()

    # task 13 handle search query
    query = request.args.get("q", "").lower()
    if query:
        notes = Note.query.filter(Note.text.ilike(f"%{query}%")).all()
    else:
        notes = Note.query.all()

    
    return render_template("notes.html", notes=notes, query=query)

#----------------------------------------------------------------
#task 8 delete
#----------------------------------------------------------------
@app.route("/delete/<int:id>")
def delete(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash("🗑️ Note delete!") #task 14
    return redirect("/notes")

#----------------------------------------------------------------
#task 11 edit
#----------------------------------------------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    note = Note.query.get_or_404(id)
    if request.method == "POST":
        note.text = request.form["note"]
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

if __name__ == "__main__":
    app.run(debug=True)

