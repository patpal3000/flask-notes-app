from flask import Flask, render_template

app = Flask(__name__)

#task 1
@app.route("/")
def home():
    return render_template("index.html")

#task 2
@app.route("/greet/<name>")
def greet(name):
    return render_template("greet.html", user=name)

if __name__ == "__main__":
    app.run(debug=True)
