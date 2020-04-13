from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_babel import Babel, gettext
from flask_assets import Environment, Bundle
from flask_oidc import OpenIDConnect
from flask_wtf import FlaskForm
from wtforms import SelectField, TextField
from datetime import datetime

import sqlite3
import pandas as pd

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'FLASK_DEBUG': 1,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_OPENID_REALM': 'http://localhost:5000/oidc_callback',
    'LANGUAGES': {
      'en': 'English',
      'es': 'Spanish'
    }
})
babel = Babel(app)
oidc = OpenIDConnect(app)
IMG_FOLDER = '/static/img/'

assets = Environment(app)
assets.url = app.static_url_path
assets.debug = True

scss = Bundle(
  'styles/about.scss',
  'styles/home.scss',
  'styles/login.scss',
  'styles/results.scss',
  'styles/start.scss',
  'styles/styles.scss',
  'styles/training.scss',
  '../templates/snippets/avatar/avatar.scss',
  '../templates/snippets/back-button/back-button.scss',
  '../templates/snippets/footer/footer.scss',
  '../templates/snippets/home-button/home-button.scss',
  filters='pyscss',
  output='styles/main.css'
)
assets.register('scss_all', scss)

@babel.localeselector
def get_locale():
    lang = request.path[1:].split('/', 1)[0]
    if lang in app.config['LANGUAGES'].keys():
        print('LANG in get_locale', lang)
        return lang
    else:
        print('DEFAULT in get_locale')
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
  
@app.before_request
def get_global_language():
    g.babel = babel
    g.language = get_locale()
    print(g.language)

def get_random_img():
    conn = sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    info = oidc.user_getinfo(['email', 'openid_id'])
    user = info.get('email')
    x = c.execute("SELECT edad, sexo, codigo, informe, diagnostico, diagnosis FROM images WHERE codigo NOT IN (SELECT image FROM user_answers WHERE  user='%s') ORDER BY random() LIMIT 1;" % user).fetchall()
    for row in x:
        img = IMG_FOLDER + row[2] +'.DCM.JPG'
        img_id = row[2]
        age = int(row[0])
        sex=gettext("Hombre")
        if int(row[1])==2:
           sex=gettext("Mujer")
        informe=int(row[3])
        diagnostico=row[4]
        diagnosis=row[5]

    conn.close()
    return age, sex, img_id, img, informe, diagnostico, diagnosis

def check_images_left():
    conn = sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    info = oidc.user_getinfo(['email', 'openid_id'])
    user = info.get('email')
    x = c.execute("SELECT COUNT(*) FROM (SELECT edad, sexo, codigo, informe FROM images WHERE codigo NOT IN (SELECT image FROM user_answers WHERE  user='%s'))" % user).fetchone()
    conn.close()
    if x[0] < 1:
        return False
    else:
        return True

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

@app.route("/")
def default_route():
    return redirect(url_for('home_'+g.language))

@app.route("/<lang>")
def lang_route(lang):
    if lang in app.config['LANGUAGES'].keys():
        print('LANG in lang_route', lang)
        return redirect(url_for('home_'+lang))
    else:
        print('DEFAULT in lang_route')
        return redirect(url_for('home_'+g.language))

@app.route("/<lang>/<page>")
def lang_route_page(lang, page):
    if lang in app.config['LANGUAGES'].keys():
        return redirect(url_for(page+'_'+lang))
    else:
        return redirect(url_for(page+'_'+g.language))

@app.route("/es", endpoint="home_es")
@app.route("/en", endpoint="home_en")
def home():
    return render_template('home.html')

@app.route("/es/about", endpoint="about_es")
@app.route("/en/about", endpoint="about_en")
def about():
    return render_template('about.html')

@app.route("/es/login", endpoint="login_es")
@app.route("/en/login", endpoint="login_en")
def login():
    if oidc.user_loggedin:
        print('User already logged in. Redirecting to next page...')
        return redirect(url_for('start_'+g.language))
    print('User not logged in. Rendering login page...')
    return render_template('login.html')

@app.route("/es/start", endpoint="start_es")
@app.route("/en/start", endpoint="start_en")
@oidc.require_login
def start():
    info = oidc.user_getinfo(['email'])
    user = info.get('email')
    print ("Deleting answers before starting the session")
    delete_answers(user)
    form = ProfileForm(request.form)
    return render_template('start.html', email=info.get('email'), form=form)

@app.route('/logout')
def logout():
    oidc.logout()
    return redirect(url_for('home_'+g.language))

@app.route('/training', methods=['GET','POST'])
@oidc.require_login
def training():
    info = oidc.user_getinfo(['email', 'openid_id'])
    user=info.get('email')
    error = ""
    if check_images_left() == False:
        print("No images left. Redirecting to results---")
        return redirect(url_for('results'))
    age, sex,  img_id, img, informe, diagnostico, diagnosis = get_random_img() #get_random
    form = TrainingForm(request.form)
    profile= ProfileForm(request.form)
    type_of_profile = profile['type_of_profile'].data
    conn = sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    c.execute("UPDATE users set profile = '%s' WHERE id  ='%s' and profile is null or profile = 'noanswer' " % (type_of_profile, user)).fetchall()
    form.img_id = img_id
    session['messages'] = {'id_image': img_id, 'img': img, 'informe': int(informe), 'diagnostico': diagnostico, 'diagnosis': diagnosis}
    if request.method == 'POST':
        type_of_diag = form.type_of_diag.data
        if type_of_diag=="pat_covid_com":
            answer=1
        elif type_of_diag=="non_pat":
            answer=0
        elif type_of_diag=="pat_no_covid_com":
            answer=2
        type_of_diag = form.type_of_diag.data
        session['user_id'] = info.get('email')
        if len(type_of_diag) == 0:
            error = "Please supply data"

    try:
        info = oidc.user_getinfo(['email', 'openid_id', 'name'])
        print("SELECT COUNT(*) FROM users WHERE id='%s'" % (info.get('email')))
        x = c.execute("SELECT COUNT(*) FROM users WHERE id='%s'" % (info.get('email')))
        row = c.fetchone()
        if row[0] == 0:
            c.execute("INSERT INTO users(id, name, email, profile) VALUES('%s', '%s', '%s', '')" % (
            info.get('email'),
            info.get('name'),
            info.get('email')))
        conn.commit()
        conn.close()        
        return render_template('training.html', form=form, message=error, age=age, sex=sex, img=img, img_id=img_id)
    except Exception as e:
        conn.close()
        print(e)
        return 'Ooops!, <a href="/start">Log in</a>'

@app.route('/send_results', methods=['POST'])
@oidc.require_login
def send_results():
    try:
        form = TrainingForm(request.form)
        type_of_diag = form['type_of_diag'].data
        answer = 0
        print("RESULT: %s" % type_of_diag)
        if type_of_diag=="pat_covid_com":
            answer=1
        elif type_of_diag=="non_pat":
            answer=0
        elif type_of_diag=="pat_no_covid_com":
            answer=2

        conn = sqlite3.connect('db/covid19.db')
        c = conn.cursor()
        info = oidc.user_getinfo(['email', 'openid_id'])
        c.execute("INSERT INTO user_answers(user, image, true_answer,answer, diagnostico, diagnosis) VALUES ('%s', '%s', %i, %i, '%s', '%s')" % (
            info.get('email'),
            session['messages']['id_image'],
            session['messages']['informe'],
            int(answer),
            session['messages']['diagnostico'],
            session['messages']['diagnosis']))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Ooops! We had a problem")
        print(e)
    return redirect(url_for('training'))

@app.route('/results')
@oidc.require_login
def results():
    conn =sqlite3.connect('db/covid19.db')
    c = conn.cursor()
    #user=session('user_id')
    info = oidc.user_getinfo(['email', 'openid_id'])
    user = info.get('email')
    x = c.execute("SELECT * FROM user_answers WHERE user = '%s'" % user).fetchall()
    failed_answers=c.execute("SELECT * FROM user_answers WHERE user = '%s' AND answer != true_answer " % user).fetchall()
    conn.close()
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
        sensitivity=gettext("Muestras insuficientes")
    try:
        specificity='%.2f'%(TN/(TN+FP))
    except:
        specificity=gettext("Muestras insuficientes")
    try:
        pos_predval='%.2f'%(TP/(TP+FP))
    except:
        pos_predval=gettext("Muestras insuficientes")
    try:
        neg_predval='%.2f'%(TN/(TN+FN))
    except:
        neg_predval=gettext("Muestras insuficientes")


    res=[total_score, sensitivity,specificity, pos_predval, neg_predval, total_answered]

    print("Deleting the answers for this session")
    delete_answers(user)
    
    return render_template('results.html', res=res, failed_answers=failed_answers,  image=session['messages']['img'])

class TrainingForm(FlaskForm):
 
    type_of_diag = SelectField(
        gettext('Selecciona diagnóstico:'),
        choices=[('pat_covid_com', gettext('Patológico (compatible con COVID-19)')),
                 ('pat_no_covid_com', gettext('Patológico (NO compatible con COVID-19)')),
                 ('non_pat', gettext('No Patológico'))])
    img_id = TextField(u'IMG ID','')

class ProfileForm(FlaskForm):
    type_of_profile = SelectField(
        'Profile',
        choices=[('noanswer', gettext('Click para seleccionar especialidad')),
                 ('abdradio', gettext('Radiólogo abdominal')),
                 ('Neuroradio', gettext('Neurorradiólogo')),
                 ('breastradio', gettext('Radiólogo de mama')),
                 ('muscradio', gettext('Radiólogo de músculo-esquelético')),
                 ('generalradio', gettext('Radiólogo general')),
                 ('interradio', gettext('Radiólogo intervencionista')),
                 ('pediradio', gettext('Radiólogo pediátrico')),
                 ('thoraradio', gettext('Radiólogo torácico')),
                 ('radioresi', gettext('Residente de radiología')),
                 ('resiother', gettext('Residente (especialidad distinta a la radiología)')),
                 ('medicalstudent', gettext('Estudiante de medicina')),
                 ('assophypulmo', gettext('Médico adjunto de neumología')),
                 ('internassisphysi', gettext('Médico adjunto internista')),
                 ('deputyemerg', gettext('Médico adjunto de urgencias')),
                 ('assodoctorother', gettext('Médico adjunto de otra especialidad')),
                 ('others', gettext('Otros'))])
