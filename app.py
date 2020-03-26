from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import SelectField, TextField
import sqlite3
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'

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
    x = c.execute("SELECT edad, id,sexo, codigo FROM images ORDER BY random() LIMIT 1;").fetchall()
    print(x)
    for row in x:
        print(row[2])
        img = IMG_FOLDER + row[3] +'.DCM.JPG'
        img_id = row[2]
        edad = row[0]
        sex="Man"
        if row[1]=="2":
           sex= "Woman"

    conn.close()
    return edad, sex, img_id, img

def delete_answers(user):
    conn =sqlite3.connect('db/covid19.db')
    c= conn.cursor()
    c.execute("DELETE FROM user_answers WHERE user = '%s'" % user)
    conn.close()
    return

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results')
def results():
    #res = check_user_answer(session['messages']['id_image'], session['messages']['user_answer'])
    conn =sqlite3.connect('db/covid19.db')
    c= conn.cursor()
    user='lara'
    x=c.execute("SELECT * FROM user_answers WHERE user = '%s'" % user).fetchall()
    total_answered=len(x)
    right_answered=0
    badly_answered=0
    TP, TN, FP, FN= 0,0,0,0
    for row in x:
        answer = row[2]
        true_answer= row[1]
        if (true_answer==1):
            true_answer="pat_covid_com"
        elif (true_answer==0):
            true_answer="no_pat"
        elif (true_answer==2):
            true_answer="pat_no_covid_com"
        #Counter for the total score

        if (true_answer==answer):
            right_answered+=1
        else:
            badly_answered+=1
        #Counter for the specificity and sensibility
        if (true_answer=="pat_covid_com" and (answer=="pat_no_covid_com" or answer=="no_pat")):
            FN+=1
        elif(true_answer=="pat_covid_com" and answer=="pat_covid_com"):
            TP+=1
        elif((true_answer=="pat_no_covid_com" or true_answer=="no_pat") and answer=="pat_covid_com"):
            FP+=1
        elif((true_answer=="pat_no_covid_com" or true_answer=="no_pat") and (answer=="pat_no_covid_com" or answer=="no_pat")):
            TN+=1


    total_score=int(100.*right_answered/total_answered)
    sensitivity=TP/(TP+FN)
    specificity=1.
    #descomentar cuando tengamos imagenes no patologicas en el dataset
    #specificity=TN/(TN+FP)
    #print("Total Score : % 1i " % (total_score) + "%")
    #print("Your specificity is : % 0.2f " % specificity)
    #print("Your sensitivity is: % 0.2f " % sensitivity)

    res=[total_score,'%.2f'%(sensitivity),'%.2f'%(specificity)]
    return render_template('results.html', res=res,  image=session['messages']['img'])

class TrainingForm(Form):
 
    type_of_diag = SelectField(
        u'Type of Diagnosis',
        choices=[('pat_covid_com', 'Patological (covid-19 compatible)'),
                 ('pat_no_covid_com', 'Patological (NO covid-19 compatible)'),
                 ('non_pat', 'Non Patological')])


@app.route('/training', methods=['GET', 'POST'])
def training():
    error = ""
    edad, sex,  img_id, img = get_random_img() #get_random
    form = TrainingForm(request.form)

    if request.method == 'POST':
        type_of_diag = form.type_of_diag.data
        session['user_id'] = 'lara'
        session['messages'] = {'id_image': img_id, 'img': img, 'user_answer' : form.type_of_diag.data}
        if len(type_of_diag) == 0:
            error = "Please supply data"
        else:
            try:
                print("Try insert")
                conn = sqlite3.connect('db/covid19.db')
                c = conn.cursor()
                print("INSERT INTO user_answers(user, image, answer) VALUES ('%s', %i, '%s')" % (session['user_id'], img_id, type_of_diag))
                c.execute("INSERT INTO user_answers(user, image, answer) VALUES ('%s', %i, '%s')" % (session['user_id'], img_id, type_of_diag))
                conn.commit()
                conn.close()
            except Exception as e:
                print("Ooops! We had a problem")
                print(e)
#            return redirect(url_for('training'))

    return render_template('training.html', form=form, message=error, edad=edad, sex=sex, img=img, img_id=img_id)

# Run the application
#app.run(debug=True)
