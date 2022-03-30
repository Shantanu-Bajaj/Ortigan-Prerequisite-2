'''importing all required packages'''
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import clx.xms
from clx.xms.api import MtBatchTextSmsCreate
import json

with open('config.json','r') as c:      #opening json file in read mode
    params = json.load(c)["params"]     #loading parameters from json file

app = Flask(__name__)               #creating a Flask object
app.config.update(                  #updating the Flask object
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['mail'],
    MAIL_PASSWORD = params['mail-pass']
)

mail = Mail(app)                    #creating an object of Mail class from flask_mail
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']         #configuring Database Parameters
db = SQLAlchemy(app)                #Creating SQLAlchemy object

class Information(db.Model):                                #creating class for database Table
    name = db.Column(db.String ,nullable = False)           #creating DM for name attribute
    email = db.Column(db.String, nullable = False)          #creating DM for email attribute
    phone = db.Column(db.Integer, primary_key = True)       #creating DM for phone attribute

@app.route("/", methods = ['GET','POST'])       #creating route for index page
def home():
    if(request.method == 'POST'):                   #checking if a request is POST or GET
        NAME = request.form.get('name')             #retrieving name entered by user in form
        EMAIL = request.form.get('email')           #retrieving email entered by user in form
        PHONE = request.form.get('phone')           #retrieving phone entered by user in form
        RECIPIENT = []                              #creating empty list of recipients
        RECIPIENT.append(EMAIL)                     #adding user's email in list
        data = Information(name = NAME, email = EMAIL, phone = PHONE)       #adding user's entered data in Database Table
        db.session.add(data)
        db.session.commit()                         #commiting session
        mail.send_message('Email',                                          #code for sending the mail with required parameters
                          sender = "shantanu.bajaj.30@gmail.com",
                          recipients = RECIPIENT,
                          body = 'Email Id has been saved')
        client = clx.xms.Client(service_plan_id='94f26b42db054f53a14de9714ced2754',     #code for sending an sms
                                token='186484640ae441d3943be18ea44c081b')
        create = clx.xms.api.MtBatchTextSmsCreate()
        create.sender = str(PHONE)
        create.recipients = {params['phone']}
        create.body = 'Name and Email has been saved for '+ PHONE

        try:
            batch = client.create_batch(create)
        except (requests.exceptions.RequestException,
                clx.xms.exceptions.ApiException) as ex:
            print('Failed to communicate with XMS: %s' % str(ex))
    return render_template('index.html')                    #rendering index page

app.run(debug=True)                 #enabling debug mode so that changes are reflected in terminal