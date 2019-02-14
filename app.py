from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from configparser import SafeConfigParser
from functools import wraps
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')

UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Config MySQL using settings.ini
config = SafeConfigParser()
config.read('settings.ini')
app.config['MYSQL_HOST'] = config.get('sql', 'MYSQL_HOST')
app.config['MYSQL_USER'] =  config.get('sql', 'MYSQL_USER')
app.config['MYSQL_PASSWORD'] = config.get('sql', 'MYSQL_PASSWORD')
app.config['MYSQL_DB'] = config.get('sql', 'MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/') # Set route for home page
def index():
    return render_template("home.html")

@app.route('/about') # Set route for about page
def about():
    return render_template("about.html")

@app.route('/scores') # Set route for scores page
def scores():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    if result > 0:
        return render_template('scores.html', articles=articles)
    else:
        msg = 'No articles found'
        return render_template('scores.html', msg=msg)
    cur.close()

@app.route('/score/<string:id>/') # Set route for individual score page
def score(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    article = cur.fetchone()
    image = None
    for file in os.listdir("./static/"):
        if file.startswith(id) and file.endswith(("png", "jpg", "jpeg")):
            image = file
    return render_template('score.html', article=article, image=image)
    app.logger.info(image)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match ya dummy')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST']) # User registration
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.data
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

@app.route('/login', methods=['POST', 'GET']) # User login
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

@app.route('/logout') # Route for logout page
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard') # Route for dashboard page
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    images = []
    for file in os.listdir("./static/"):
        imgid = file.split('.')[0]
        images.append(int(imgid))
    if result > 0:
        return render_template('dashboard.html', articles=articles, images=images)
    else:
        msg = 'No articles found'
        return render_template('dashboard.html', msg=msg, images=images)
    cur.close()

class ArticleForm(Form): # Submit Article (replace with scores later)
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=1)])

@app.route('/add_article', methods=["GET", "POST"]) # Route for add article page
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        id = cur.lastrowid
        mysql.connection.commit()
        cur.close()
        try:
            file = request.files['file']
        except:
            flash('No file uploaded')
            file = None
        if file != None:
            if file.filename == '':
                flash('No file selected!')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                fileext = file.filename.split('.')[-1]
                filename = secure_filename(str(id) + ".{}".format(fileext))
                file.save(os.path.join("./static".format(id), filename))
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('verify_article', id=id))
        flash('Score submitted!', 'success')
    return render_template('add_article.html', form=form)

@app.route('/edit_article/<string:id>', methods=["GET", "POST"]) # Route for edit article page
@is_logged_in
def edit_article(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = cur.fetchone()

    form = ArticleForm(request.form)
    form.title.data = article['title']
    form.body.data = article['body']
    if request.method == "POST" and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE article SET title = %s, body = %s WHERE id = %s", (title, body, id))
        mysql.connection.commit()
        cur.close()
        flash('Score edited!', 'success')
    return render_template('edit_article.html', form=form)

@app.route('/verify_article/<string:id>', methods=["GET", "POST"]) # Route for edit article page
@is_logged_in
def verify_article(id):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected!')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            fileext = file.filename.split('.')[-1]
            filename = secure_filename((id) + ".{}".format(fileext))
            file.save(os.path.join("./static".format(id), filename))
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('verify_article', id=id))
    return render_template('verify_article.html')

@app.route('/delete_article/<string:id>/', methods=["POST"]) # Route for delete artricle page
@is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()
    flash('Score deleted!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key = config.get('settings', 'secretkey')
    app.run(debug=True)
