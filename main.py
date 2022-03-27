import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import clx.xms
from clx.xms.api import MtBatchTextSmsCreate
import json

with open('config.json','r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['mail'],
    MAIL_PASSWORD = params['mail-pass']
)

mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
db = SQLAlchemy(app)

class Information(db.Model):
    name = db.Column(db.String ,nullable = False)
    email = db.Column(db.String, nullable = False)
    phone = db.Column(db.Integer, primary_key = True)

@app.route("/", methods = ['GET','POST'])
def home():
    if(request.method == 'POST'):
        '''Adding entry to database'''
        NAME = request.form.get('name')
        EMAIL = request.form.get('email')
        PHONE = request.form.get('phone')
        data = Information(name = NAME, email = EMAIL, phone = PHONE)
        db.session.add(data)
        db.session.commit()
        mail.send_message('Email',
                          sender = EMAIL,
                          recipients = [params['mail']],
                          body = 'Email Id has been saved')
        client = clx.xms.Client(service_plan_id='94f26b42db054f53a14de9714ced2754',
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
    return render_template('index.html')

app.run(debug=True)