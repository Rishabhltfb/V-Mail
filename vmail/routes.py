import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from vmail import app, db, bcrypt
from vmail.forms import RegistrationForm, LoginForm, MailForm
from vmail.models import User, Mail
from flask_login import login_user, current_user, logout_user, login_required
import speech_recognition as sr
import pythoncom
import win32com.client as wincl
import time


r = sr.Recognizer()


def tts(text):
    speak = wincl.Dispatch("SAPI.SpVoice")
    speak.Speak(text)


def listen_speech():
    with sr.Microphone() as source:
        tts("Speak Anything")
        print("Speak Anything :")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You : {}".format(text))
            tts("You said :" + text)
        except:
            print("Sorry could not recognize your voice.")
            tts("Sorry could not recognize your voice.")
            listen_speech()
    return text


@app.route("/")
def cover():
    cover_img = url_for('static', filename='media/cover.jpg')
    return render_template('cover.html', cover_img=cover_img)


@app.route("/inbox")
def inbox():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    mails = Mail.query.filter_by(receiver_id=user.id).order_by(
        Mail.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('inbox.html', mails=mails)


@app.route("/sent_mail")
def sent_mail():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    mails_use = Mail.query.filter_by(
        author=user).order_by(Mail.date_posted.desc())
    receivers = []
    for mail in mails_use:
        receiver = User.query.filter_by(id=mail.receiver_id).first_or_404()
        receivers.append(receiver)

    mails = Mail.query.filter_by(author=user).order_by(
        Mail.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('sent_mail.html', mails=mails, receivers=receivers)


@app.route("/mail/<int:mail_id>")
def mail(mail_id):
    mail = Mail.query.get_or_404(mail_id)
    pythoncom.CoInitialize()
    tts("From :" + mail.author.username)
    tts("Date :" + str(mail.date_posted.strftime('%Y-%m-%d')))
    tts("Subject :" + mail.title)
    tts("Content :" + mail.content)
    return render_template('mail.html', title=mail.title, mail=mail)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('inbox'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inbox'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('inbox'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('cover'))


@app.route("/mail/new", methods=['GET', 'POST'])
@login_required
def new_mail():
    form = MailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.receiver.data).first()
        receiver_id = user.id
        mail = Mail(title=form.title.data,
                    content=form.content.data, author=current_user, receiver_id=receiver_id)
        db.session.add(mail)
        db.session.commit()
        flash('Your mail has been sent!', 'success')
        return redirect(url_for('inbox'))
    return render_template('create_mail.html', title='New Mail',
                           form=form, legend='New Mail')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
