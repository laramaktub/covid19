from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import SelectField, TextField
import sqlite3
import pandas as pd
import sqlite3

print("Try insert")
conn = sqlite3.connect('db/covid19.db')
c = conn.cursor()
x = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(x)

x = c.execute("PRAGMA table_info(user_answers);").fetchall()
print(x)

x = c.execute("SELECT * FROM user_answers;").fetchall()
print(x)

x= c.execute("DELETE FROM user_answers WHERE user = 'aguilarf';").fetchall()
#c.execute("INSERT INTO users(user, id)  VALUES ('%s', %i)" % ("lara", 2))

####RESULTADOS#####

user='lara'
x=c.execute("SELECT * FROM user_answers WHERE user = '%s'" % user).fetchall()
total_answered=len(x)
print(total_answered)
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

print(FN)
print(TP)
print(FP)
print(TN)

total_score=int(100.*right_answered/total_answered)
sensitivity=TP/(TP+FN)
#specificity=TN/(TN+FP)
print("Total Score : % 1i " % (total_score) + "%")
#print("Your specificity is : % 0.2f " % specificity)
print("Your sensitivity is: % 0.2f " % sensitivity)
conn.commit()
conn.close()

