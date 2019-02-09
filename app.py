from flask import Flask, render_template
from data import Scores

app = Flask(__name__)

Scores = Scores()

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/scores')
def scores():
    return render_template("scores.html", scores=Scores)

@app.route('/score/<string:id>/')
def score(id):
    return render_template('score.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)
