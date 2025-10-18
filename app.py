from flask import Flask, render_template, request, redirect
import json, os

app = Flask(__name__)

#task 1
@app.route("/")
def home():
    return render_template("index.html")

#task 2
@app.route("/greet/<name>")
def greet(name):
    return render_template("greet.html", user=name)

#task 3
@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["username"]
    return render_template("thanks.html", name=name)

#task 4
@app.route("/about")
def about():
    return render_template("about.html")

#task 5
@app.route("/profile")
def profile():
    user = {
        "name": "RDH",
        "age": 25,
        "hobby": "coding"
    }
    return render_template("profile.html", user=user)

#task 6
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        message = request.form["message"]
        return render_template("feedback.html", respone=message)
    return render_template("feedback.html", respone=None)

#task 10 read and update
def load_notes():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open("data.json", "w") as f:
        json.dump(notes, f, indent=2)

#task 7 create
notes = []
@app.route("/notes", methods=["GET", "POST"])
def notes_page():
    notes = load_notes() #task 10

    # add new note
    if request.method == "POST":
        note = request.form["note"]
        #notes.append(note)
        if note.strip():
            notes.append(note)
            save_notes(notes)

    # task 13 handle search query
    query = request.args.get("q", "").lower()
    if query:
        notes = [n for n in notes if query in n.lower()]

    return render_template("notes.html", notes=notes, query=query)

#task 8 delete
@app.route("/delete/<int:index>")
def delete(index):
    notes = load_notes() #task 10
    if 0 <= index < len(notes):
        notes.pop(index)
        save_notes(notes) #task 10
    return redirect("/notes")

#task 11 update
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    notes = load_notes()
    if request.method == "POST":
        new_text = request.form["note"]
        notes[index] = new_text
        save_notes(notes)
        return redirect("/notes")
    return render_template("edit.html", note=notes[index])

if __name__ == "__main__":
    app.run(debug=True)

