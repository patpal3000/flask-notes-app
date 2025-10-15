from flask import Flask, render_template, request

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

if __name__ == "__main__":
    app.run(debug=True)
