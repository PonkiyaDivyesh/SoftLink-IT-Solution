from re import sub
from threading import local
from flask import Flask, render_template, jsonify, session
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
# from werkzeug import secure_filename
from werkzeug.utils import secure_filename
import json
import os
from flask_mail import Mail
from datetime import datetime
import math

import socket

from werkzeug.utils import redirect
socket.getaddrinfo('localhost', 8080)


with open ('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['UPLOAD_FOLDER'] = params['upload_locaion']

app.config.update(
    MAIL_SERVER ='smtp.gamil.com',
    MAIL_PORT ='465',
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
db = SQLAlchemy(app)

class Contact(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subject = db.Column(db.String(120), unique=True, nullable=False)
    msg = db.Column(db.String(120), unique=True, nullable=False)
    datetime = db.Column(db.String(120), unique=True, nullable=True)

class Faq(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(20), unique=True, nullable=False)
    answer = db.Column(db.String(200), unique=True, nullable=False)
    date = db.Column(db.String(120), unique=True, nullable=True)

class Team(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    post = db.Column(db.String(50), unique=True, nullable=False)
    intro = db.Column(db.String(100), unique=True, nullable=False)
    b_intro = db.Column(db.String(300), unique=True, nullable=False)
    twit = db.Column(db.String(50), unique=True, nullable=False)
    fb = db.Column(db.String(50), unique=True, nullable=False)
    insta = db.Column(db.String(50), unique=True, nullable=False)
    linkedin = db.Column(db.String(50), unique=True, nullable=False)
    image = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(20), unique=True, nullable=False)
    datetime = db.Column(db.String(120), unique=True, nullable=True)

    def __init__(self, name, email, subject, msg, datetime):
            self.name = name
            self.email = email
            self.subject =subject
            self.msg =msg
            self.datetime =datetime
    
    # def __repr__(self) -> str:
    #      return f"{self.srno} - {self.title} - {self.title} - {self.title} - {self.title} - {self.title}"

    

@app.route("/")
def index():
    return render_template('index.html', params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/services/", methods=['GET'])
def services():
    team = Team.query.filter_by().all()
    return render_template('services.html', params=params, team=team)

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html', params=params)

@app.route("/team/", methods=['GET'])
def team_post():
    team = Team.query.filter_by().all()
    return render_template('team.html', params=params, team=team)

@app.route("/teamdetails/<string:team_slug>", methods=['GET'])
def teamdetails_post(team_slug):
    team = Team.query.filter_by(slug=team_slug).first()
    return render_template('teamdetails.html', params=params, team=team)

@app.route("/pricing")
def pricing():
    return render_template('pricing.html', params=params)

@app.route("/faq/", methods=['GET'])
def faq_route():
    faq = Faq.query.filter_by().all()
    last = math.ceil(len(faq)/int(params['no_of_faq']))

    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    
    faq = faq[(page-1)*int(params['no_of_faq']) : (page-1)*int(params['no_of_faq']) + int(params['no_of_faq'])]

    if (page==1):
        prev = "#"
        next = "/faq/?page=" + str(page + 1)
    elif(page==last):
        prev = "/faq/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/faq/?page=" + str(page - 1)
        next = "/faq/?page=" + str(page + 1)

    return render_template('faq.html', params=params, faq=faq, prev=prev, next=next)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        entry = Contact(name = name, email = email, subject=subject, msg = message, datetime = datetime.now())
        db.session.add(entry)
        db.session.commit()

        mail.send_message('New Msg From' + name, 
                            sender = email,
                            recipients = [params['gmail-user']],
                            body = subject + "\n" + message)

    return render_template('contact.html', params=params)

# @app.route("/innerpage")
# def innerpage():
#     return render_template('innerpage.html', params=params)
    
# @app.route("/protfoliodetails")
# def protfoliodetails():
#     return render_template('portfoliodetails.html', params=params)


# Admin Panel Pages

@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method=='POST':
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))

        return "Uploaded successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/singin")
def singin():
    return render_template('singin.html', params=params)

@app.route("/dashboard/", methods=['GET', 'POST'])
def dashboard():
        if ('user' in session and session['user'] == params['admin_user']):
            return render_template('dashboard.html', params=params)

        if request.method=='POST':
            username = request.form.get('uname')
            userpass = request.form.get('upass')

            if (username == params['admin_user'] and userpass == params['admin_pass'] ):
                session['user'] = username
                return render_template('dashboard.html', params=params)
            

        return render_template('login.html', params=params)

@app.route("/afaq/", methods=['GET', 'POST'])
def afaq():
        if ('user' in session and session['user'] == params['admin_user']):
            faq = Faq.query.filter_by().all()
            return render_template('afaq.html', params=params, faq=faq)

        if request.method=='POST':
            username = request.form.get('uname')
            userpass = request.form.get('upass')

            if (username == params['admin_user'] and userpass == params['admin_pass'] ):
                session['user'] = username
                faq = Faq.query.filter_by().all()
                return render_template('afaq.html', params=params, faq=faq)
            

        return render_template('login.html', params=params)

@app.route("/editfaq/<string:sno>", methods=['GET', 'POST'])
def editfaq(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method=='POST':
            question = request.form.get('question')
            slug = request.form.get('slug')
            answer = request.form.get('answer')
            date = datetime.now()

            if sno=='0':
                faq = Faq(question=question, slug=slug, answer=answer, date=date)
                db.session.add(faq)
                db.session.commit()

            else:
                faq = Faq.query.filter_by(sno=sno).first()
                faq.question = question
                faq.slug = slug
                faq.answer = answer
                faq.date = date
                db.session.commit()

                return redirect('/editfaq/' + sno)

        faq = Faq.query.filter_by(sno=sno).first()
        return render_template('editfaq.html', params=params, faq=faq, sno=sno)
         
    return redirect('/dashboard')
    

@app.route('/deletefaq/<int:sno>')
def deletefaq(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        faq = Faq.query.filter_by(sno=sno).first()
        db.session.delete(faq)
        db.session.commit()

    return redirect('/afaq')

if __name__ == "__main__":
    app.run(debug=True, port=1000)