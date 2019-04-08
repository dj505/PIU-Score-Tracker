from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, IntegerField, validators
from passlib.hash import sha256_crypt
from configparser import SafeConfigParser
from functools import wraps
import operator
import os
from werkzeug.utils import secure_filename
import loadsongs
from json import load, dump, loads, dumps

# TODO:
# - Clean up this mess
# - Add more/multiple filters
# - Add support for more games

application = Flask(__name__, static_url_path='/static')

UPLOAD_FOLDER = './static/scores'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Config MySQL using settings.ini
config = SafeConfigParser()
config.read('settings.ini')
application.config['MYSQL_HOST'] = config.get('sql', 'MYSQL_HOST')
application.config['MYSQL_USER'] =  config.get('sql', 'MYSQL_USER')
application.config['MYSQL_PASSWORD'] = config.get('sql', 'MYSQL_PASSWORD')
application.config['MYSQL_DB'] = config.get('sql', 'MYSQL_DB')
application.config['MYSQL_CURSORCLASS'] = "DictCursor"

difficulties = []
for i in range(1, 29):
    difficulties.append(i)
difficulties = list(zip(difficulties, difficulties))

songlist_pairs = loadsongs.load_song_lists()
mysql = MySQL(application)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route('/') # Set route for home page
def index():
    return render_template("home.html")

@application.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    if request.method == "POST" and form.validate():
        session['song_search'] = form.song.data
        session['filters'] = form.filters.data
        return redirect(url_for('search_results'))
    return render_template("search.html", songlist=songlist_pairs, form=form)

@application.route('/search_results/')
def search_results():
    application.logger.info(session['song_search'])
    song = session['song_search']
    filter = session['filters']
    if filter == "score" or filter == "difficulty":
        query = 'SELECT * FROM piu WHERE song = "{}"'.format(song)
    if filter == "stagepass":
        query = 'SELECT * FROM piu WHERE song = "{}" AND stagepass = 1'.format(song)
    if filter == "stagebreak":
        query = 'SELECT * FROM piu WHERE song = "{}" AND stagepass = 0'.format(song)
    if filter == "ranked":
        query = 'SELECT * FROM piu WHERE song = "{}" AND ranked = 1'.format(song)
    if filter == "unranked":
        query = 'SELECT * FROM piu WHERE song = "{}" AND ranked = 0'.format(song)
    if filter == "pad":
        query = 'SELECT * FROM piu WHERE song = "{}" AND platform = "pad"'.format(song)
    if filter == "keyboard":
        query = 'SELECT * FROM piu WHERE song = "{}" AND platform = "keyboard"'.format(song)
    cur = mysql.connection.cursor()
    result = cur.execute(query)
    results = cur.fetchall()
    results = list(results)
    if filter != "difficulty":
        results = sorted(results, key=lambda tup: tup['score'], reverse=True)
    else:
        results = sorted(results, key=lambda tup: int(tup['difficulty']), reverse=True)
    if len(results) > 0:
        for result in results:
            result['lvl_prefix'] = result['type'][0].upper()
            result['difficulty'] = str(result['difficulty'])
            result['lettergrade'] = result['lettergrade'].upper()
            result['platform'] = result['platform'].capitalize()
            if result['stagepass'] == 1:
                result['stagepass'] = "Yes"
            elif result['stagepass'] == 0:
                result['stagepass'] = "No"
            if result['ranked'] == 0:
                result['ranked'] = "Unranked"
            elif result['ranked'] == 1:
                result['ranked'] = "Ranked"
            else:
                result['ranked'] = "Unknown"
    return render_template("search_results.html", results=results)

@application.route('/about') # Set route for about page
def about():
    return render_template("about.html")

@application.route('/scores') # Set route for scores page
def scores():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM piu")
    scores = cur.fetchall()
    images = []
    for file in os.listdir("./static/scores"):
        imgid = file.split('.')[0]
        images.append(int(imgid))
    if result > 0:
        for score in scores:
            score['lettergrade'] = score['lettergrade'].upper()
            score['platform'] = score['platform'].capitalize()
            score['difficulty'] = str(score['difficulty'])
            score['lvl_prefix'] = score['type'][0].upper()
            if score['stagepass'] == 1:
                score['stagepass'] = "Yes"
            elif score['stagepass'] == 0:
                score['stagepass'] = "No"
            if score['ranked'] == 0:
                score['ranked'] = "Unranked"
            elif score['ranked'] == 1:
                score['ranked'] = "Ranked"
            else:
                score['ranked'] = "Unknown"
        return render_template('scores.html', scores=scores, images=images)
        application.logger.info(scores)
    else:
        msg = 'No articles found'
        return render_template('scores.html', msg=msg)
    cur.close()

@application.route('/score/<string:id>/') # Set route for individual score page
def score(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM piu WHERE id=%s", [id])
    score = cur.fetchone()
    image = None
    score['type'] = score['type'].capitalize()
    score['lettergrade'] = score['lettergrade'].upper()
    if score['stagepass'] == 1:
        score['stagepass'] = "Yes"
    elif score['stagepass'] == 0:
        score['stagepass'] = "No"
    if score['ranked'] == 0:
        score['ranked'] = "Unranked"
    elif score['ranked'] == 1:
        score['ranked'] = "Ranked"
    else:
        score['ranked'] = "Unknown"
    for file in os.listdir("./static/scores"):
        if file.startswith(id) and file.endswith(("png", "jpg", "jpeg")):
            image = file
    return render_template('score.html', score=score, image=image)
    application.logger.info(image)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match ya dummy')
    ])
    confirm = PasswordField('Confirm Password')

@application.route('/register', methods=['GET', 'POST']) # User registration
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor() # Creates cursor
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        mysql.connection.commit() # Commits the above change to the database
        cur.close() # Closes the connection

        flash('You have been registered successfully! You may now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@application.route('/login', methods=['POST', 'GET']) # User login
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You have been logged in successfully!')
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid login."
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = "Username not found."
            return render_template('login.html', error=error)
    return render_template('login.html')

def is_logged_in(f): # Decorator to check if user is logged in
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to view this!', 'danger')
            return redirect(url_for('login'))
    return wrap

@application.route('/logout') # Route for logout page
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@application.route('/dashboard') # Route for dashboard page
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    _sql = "SELECT * FROM piu WHERE author='{0}'"
    result = cur.execute(_sql.format(session['username']))
    scores = cur.fetchall()
    images = []
    for file in os.listdir("./static/scores"):
        imgid = file.split('.')[0]
        images.append(int(imgid))
    if result > 0:
        return render_template('dashboard.html', scores=scores, images=images)
    else:
        msg = 'No articles found'
        return render_template('dashboard.html', msg=msg, images=images)
    cur.close()

class ArticleForm(Form): # Submit Article (replace with scores later)
    song = SelectField('Song', coerce=str, choices=songlist_pairs)
    lettergrade = SelectField('Letter Grade', coerce=str, choices=(('f', 'F'), ('d', 'D'), ('c', 'C'), ('b', 'B'), ('a', 'A'), ('s', 'S'), ('ss', 'SS'), ('sss', 'SSS')))
    score = IntegerField('Score')
    stagepass = SelectField('Stage Pass', coerce=str, choices=(('1', 'True'), ('0', 'False')))
    type = SelectField('Type', coerce=str, choices=(('singles', 'Singles'), ('doubles', 'Doubles')))
    difficulty = SelectField('Difficulty', coerce=int, choices=difficulties)
    platform = SelectField('Platform', coerce=str, choices=(('pad', 'Pad'), ('keyboard', 'Keyboard')))
    ranked = SelectField('Ranked?', coerce=str, choices=(('1', 'Ranked'), ('0', 'Unranked')))

class SearchForm(Form):
    filters = (
    ("score", "Score"),
    ("difficulty", "Difficulty"),
    ("stagepass", "Stage Pass"),
    ("stagebreak", "Stage Break"),
    ("ranked", "Ranked"),
    ("unranked", "Unranked"),
    ("pad", "Pad"),
    ("keyboard", "Keyboard")
    )
    song = SelectField('Song', coerce=str, choices=songlist_pairs)
    filters = SelectField('Filter', coerce=str, choices=filters)

class ArticleEditForm(Form): # Submit Article (replace with scores later)
    body = TextAreaField('Body', [validators.Length(min=1)])

class ClaimForm(Form):
    song = SelectField('Song', coerce=str, choices=songlist_pairs)

@application.route('/add_article', methods=["GET", "POST"]) # Route for add article page
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        song = form.song.data
        lettergrade = form.lettergrade.data
        score = form.score.data
        stagepass = form.stagepass.data
        type = form.type.data
        difficulty = form.difficulty.data
        platform = form.platform.data
        ranked = form.ranked.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO piu(song, lettergrade, score, stagepass, type, difficulty, author, platform, ranked) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (song, lettergrade, score, stagepass, type, difficulty, session['username'], platform, ranked))
        id = cur.lastrowid
        mysql.connection.commit()
        cur.close()
        try:
            file = request.files['file']
        except:
            flash('No file uploaded', 'info')
            file = None
        if file != None:
            if file.filename == '':
                flash('No file selected!', 'error')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                fileext = file.filename.split('.')[-1]
                filename = secure_filename(str(id) + ".{}".format(fileext.lower()))
                file.save(os.path.join("./static/scores".format(id), filename))
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('scores', id=id))
            elif file and not allowed_file(file.filename):
                flash('You can\'t upload that!', 'error')
        flash('Score submitted!', 'success')
        return redirect(url_for('scores', id=id))
    return render_template('add_article.html', form=form)

@application.route('/verify_article/<string:id>', methods=["GET", "POST"]) # Route for edit article page
@is_logged_in
def verify_article(id):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected!')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            fileext = file.filename.split('.')[-1]
            filename = secure_filename((id) + ".{}".format(fileext.lower()))
            file.save(os.path.join("./static/scores".format(id), filename))
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('verify_article', id=id))
        elif file and not allowed_file(file.filename):
                flash('You can\'t upload that!', 'error')
    return render_template('verify_article.html')

@application.route('/delete_article/<string:id>/', methods=["POST"]) # Route for delete artricle page
@is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM piu WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()
    flash('Score deleted!', 'success')
    return redirect(url_for('dashboard'))

@application.route('/claim', methods=["GET"]) # Route for delete artricle page
@is_logged_in
def claim():
    temps = []
    for file in os.listdir("discordbot/discorddata"):
        if file.startswith("temp"):
            print(file[:5])
            temps.append(file)
    return render_template('claim.html', temps=temps)

@application.route('/claim_score/<string:temp>', methods=["POST", "GET"]) # Route for delete artricle page
@is_logged_in
def claim_score(temp):
    form = ClaimForm(request.form)
    with open("discordbot/discorddata/{}.json".format(temp)) as f:
        json = load(f)
        print(json)
    if "image" not in json:
        json["image"] = None
    for file in os.listdir("discordbot/discorddata"):
        if file.split(".")[-1] in ['png','PNG','jpg','JPG','jpeg','JPEG'] and file.startswith(json["image"].split(".")[0]):
            fileext = file.split(".")[-1]
    if request.method == "POST" and form.validate():
        song = form.song.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO piu(song, lettergrade, score, stagepass, type, difficulty, author, platform, ranked) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (song, json["lettergrade"], json["score"], json["stagepass"], json["type"], json["difficulty"], session['username'], json["platform"], json["ranked"]))
        id = cur.lastrowid
        mysql.connection.commit()
        cur.close()
        os.remove("discordbot/discorddata/{}.json".format(temp))
        os.rename("discordbot/discorddata/{}.{}".format(temp.split("temp")[-1], fileext), "static/scores/{}.{}".format(id, fileext))
        flash('Score claimed!', 'success')
        return redirect(url_for("dashboard"))
    return render_template('claim_score.html', form=form, json=json, image=json["image"], replacements={"0": "Unranked", "1": "Ranked"})

if __name__ == '__main__':
    application.secret_key = config.get('settings', 'secretkey')
    application.run(debug=True, host="0.0.0.0", port=80) #, ssl_context=('cert.pem', 'key.pem')
