from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, IntegerField, validators
import loadsongs

difficulties = []
for i in range(1, 29):
    difficulties.append(i)
difficulties = list(zip(difficulties, difficulties))

songlist_pairs = loadsongs.load_song_lists()

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match ya dummy')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired()])

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
