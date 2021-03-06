import os
from os import path
from flask import Flask, render_template, url_for, request, flash, current_app, redirect, session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_bootstrap import Bootstrap
from flask_wtf import Form, FlaskForm
from flask_mail import Message, Mail
from flask_moment import Moment
from wtforms import TextField, TextAreaField, SubmitField, SelectField, ValidationError, StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, DataRequired, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, fresh_login_required, logout_user, current_user
from datetime import datetime
import stripe

stripe_keys = {
  'secret_key': 'pk_test_87AxnNnWKK2upOoR1OynsXVw00ZhJONDsj',
  'publishable_key': 'sk_test_OuQ7AMk9hVz9DdhdwlLPdHrs00gkRO4CCJ'
}

stripe.api_key = stripe_keys['secret_key']

Mail=Mail()
Moment= Moment()
LoginManager = LoginManager()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
bootstrap = Bootstrap(app)


DEBUG=False



app.config.from_object(__name__)
app.config['SECRET_KEY']='123456789_ABC'
db_path = os.path.join(os.path.dirname(__file__), 'users.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['CSRF_ENABLED']= True

#no money to buy server...
app.config['SERVER_NAME']='localhost:5000'
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'mikazuki599@gmail.com'
app.config["MAIL_PASSWORD"] = '123456789_ABC'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


Mail.init_app(app)
Moment.init_app(app)
LoginManager.init_app(app)
db.create_all()


LoginManager.session_protection = 'strong'
LoginManager.login_view = 'login'
LoginManager.login_message='You need to login!'



class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('There is account with that email. Please use different account.')

class ContactForm(Form):
    FirstName= TextField("FirstName", validators=[InputRequired("Please")])
    LastName = TextField("LastName", validators=[DataRequired()])
    Email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    Message = TextAreaField("Message")
    Submit = SubmitField("Submit")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


@LoginManager.user_loader
def LoadUser(UserId):
    return User.query.get(int(UserId))

@app.route('/')
def Welcome():
    return redirect('/Home')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http','https')and \
           ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                session['username'] = user.username
                session['email']= user.email
                return redirect(url_for('Home'))

        return '<h1>Invalid email or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def LogOut():
    logout_user()
    return redirect ('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return render_template('NewUserCreated.html')
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='mikazuki599@gmail.com',
                  recipients=[user.email])
    msg.body = user.username+ f''' To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    Mail.send(msg)

@app.route('/test')
def test():
    return render_template('layout.html')


@app.route("/password", methods=['GET', 'POST'])
def password():
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('forget-password.html', title='Reset Password', form=form)


@app.route("/password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('resetToken.html', title='Reset Password', form=form)



@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about_us')
def about_us():
    return render_template('about.html')

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms-of-service.html')


@app.route('/contact_us',methods=['GET','POST'])
def contact():
    form = ContactForm(request.form)
    if request.method =='POST':
        if form.validate==False:
            flash('All fields are required.')
            return render_template('contact.html',form=form)
        else:
             msg = Message(sender=form.Email.data, recipients=['abeansroastery@gmail.com'])
             msg.body = """
             From: %s %s; %s ;
             %s
             """ % (form.FirstName.data, form.LastName.data,form.Email.data, form.Message.data)
             Mail.send(msg)

             return render_template('contact.html', success=True)

    elif request.method == 'GET':
        return render_template('contact.html',form=form)



if __name__=="__main__":
    db.create_all()
    app.run(debug=True)
