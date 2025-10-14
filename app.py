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

if __name__ == "__main__":
    app.run(debug=True)
