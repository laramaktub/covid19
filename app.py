from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from flask_oidc import OpenIDConnect
from wtforms import SelectField, TextField
from datetime import datetime
import sqlite3
import pandas as pd

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_OPENID_REALM': 'http://localhost:5000/oidc_callback'
})
oidc = OpenIDConnect(app)
IMG_FOLDER = '/static/img/'

def check_user_answer(id_image, user_answer):
    print("Select id_image and get type")
    print("IF user answer is equal to image type")
    result = "Result is OK"
    print("IF not")
    result = "This image is type Patological (covid-19 compatible)"
    return result 

def get_random_img():
    conn = sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    x = c.execute("SELECT edad, sexo,codigo, informe FROM images ORDER BY random() LIMIT 20;").fetchall()
    for row in x:
        img = IMG_FOLDER + row[2] +'.DCM.JPG'
        img_id = row[2]
        edad = int(row[0])
        sex="Man"
        if int(row[1])==2:
           sex= "Woman"
        informe=int(row[3])

    conn.close()
    return edad, sex, img_id, img, informe

def delete_answers(user):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    conn = sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    x = c.execute("SELECT user, image, true_answer,  answer FROM user_answers WHERE user = '%s'" % user).fetchall()
    for row in x:
        print("INSERT INTO historic_answers(user, image, ans_date, true_answer, answer) VALUES('%s', '%s', '%s', %i, %i)" % (row[0], row[1], dt_string, row[2], row[3]))
        c.execute("INSERT INTO historic_answers(user, image, ans_date, true_answer, answer) VALUES('%s', '%s', '%s', %i, %i)" % (row[0], row[1], dt_string, row[2], row[3]))
    c.execute("DELETE FROM user_answers WHERE user = '%s'" % user)
    conn.commit()
    conn.close()
    return

@app.route('/')
def index():
    if oidc.user_loggedin:
        return ('Hello, %s, <a href="/logged">See private</a> '
                '<a href="/logout">Log out</a>') % \
            oidc.user_getfield('email')
    else:
        return 'Welcome anonymous, <a href="/logged">Log in</a>'

@app.route('/logged')
@oidc.require_login
def logged():
    info = oidc.user_getinfo(['email', 'openid_id'])
    return render_template('logged.html', email=info.get('email'), openid_id=info.get('openid_id'))

@app.route('/logout')
def logout():
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'

@app.route('/results')
@oidc.require_login
def results():
    #res = check_user_answer(session['messages']['id_image'], session['messages']['user_answer'])
    conn =sqlite3.connect('db/covid19.db')
    c= conn.cursor()
    #user=session('user_id')
    info = oidc.user_getinfo(['email', 'openid_id'])
    user = info.get('email')
    x=c.execute("SELECT * FROM user_answers WHERE user = '%s'" % user).fetchall()
    failed_answers=c.execute("SELECT * FROM user_answers WHERE user = '%s' AND answer != true_answer " % user).fetchall()
    total_answered=len(x)
    right_answered=0
    badly_answered=0
    TP, TN, FP, FN= 0,0,0,0
    for row in x:
        answer = row[3]
        true_answer= row[2]
        #counter for the total score
        if (true_answer==answer):
            right_answered+=1
        else:
            badly_answered+=1
        #Counter for the specificity and sensibility
        if (true_answer==1 and (answer==2 or answer==0)):
            FN+=1
        elif(true_answer==1 and answer==1):
            TP+=1
        elif((true_answer==2 or true_answer==0) and answer==1):
            FP+=1
        elif((true_answer==2 or true_answer==0) and (answer==2 or answer==0)):
            TN+=1


    if (total_answered==0):
        total_score="You have to try with more samples. Your total number of answered questions is 0"
    else:
        total_score=int(100.*right_answered/total_answered)
    try:
        sensitivity='%.2f'%(TP/(TP+FN))
    except:
        sensitivity="NaN --> Try again with more samples"
    try:
        specificity='%.2f'%(TN/(TN+FP))
    except:
        specificity="NaN --> Try again with more samples"

    res=[total_score, sensitivity,specificity]

    print("Deleting the answers for this session")
    delete_answers(user)
    
    return render_template('results.html', res=res, failed_answers=failed_answers,  image=session['messages']['img'])

class TrainingForm(Form):
 
    type_of_diag = SelectField(
        u'Type of Diagnosis',
        choices=[('pat_covid_com', 'Patological (covid-19 compatible)'),
                 ('pat_no_covid_com', 'Patological (NO covid-19 compatible)'),
                 ('non_pat', 'Non Patological')])


@app.route('/training', methods=['GET', 'POST'])
@oidc.require_login
def training():
    error = ""
    edad, sex,  img_id, img, informe = get_random_img() #get_random
    form = TrainingForm(request.form)
    if request.method == 'POST':
        type_of_diag = form.type_of_diag.data
        if type_of_diag=="pat_covid_com":
            answer=1
        elif type_of_diag=="non_pat":
            answer=0
        elif type_of_diag=="pat_no_covid_com":
            answer=2
        type_of_diag = form.type_of_diag.data
        info = oidc.user_getinfo(['email', 'openid_id'])
        session['user_id'] = info.get('email')
        session['messages'] = {'id_image': img_id, 'img': img, 'user_answer' : form.type_of_diag.data}
        if len(type_of_diag) == 0:
            error = "Please supply data"
        else:
            try:
                print("Try insert")
                conn = sqlite3.connect('db/covid19.db')
                c = conn.cursor()
                print("INSERT INTO user_answers(user, image, true_answer, answer) VALUES ('%s', '%s', '%i', '%i')" % (session['user_id'], img_id, int(informe), int(answer)))
                c.execute("INSERT INTO user_answers(user, image, true_answer,answer) VALUES ('%s', '%s', '%i', '%i')" % (session['user_id'], img_id, int(informe), int(answer)))
                conn.commit()
                conn.close()
            except Exception as e:
                print("Ooops! We had a problem")
                print(e)
#            return redirect(url_for('training'))

    try:
        info = oidc.user_getinfo(['email', 'openid_id'])
        conn = sqlite3.connect('db/covid19.db')
        c = conn.cursor()
        print("SELECT COUNT(*) FROM users WHERE id='%s'" % (info.get('email')))
        x = c.execute("SELECT COUNT(*) FROM users WHERE id='%s'" % (info.get('email')))
        row = c.fetchone()
        if row[0] > 0:
            return render_template('training.html', form=form, message=error, edad=edad, sex=sex, img=img, img_id=img_id)
        else:
            return 'You are not an allowed user'
        conn.close()
    except Exception as e:
        conn.close()
        print(e)
        return 'Ooops!, <a href="/logged">Log in</a>'

# Run the application
#app.run(debug=True)
