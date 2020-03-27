from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import Form
from wtforms import SelectField, TextField
import sqlite3
import pandas as pd

conn = sqlite3.connect('db/covid19.db')
c = conn.cursor()

user="lara"
#x=c.execute("SELECT * FROM user_answers WHERE user = '%s' AND answer = 'pat_covid_com' " % user).fetchall()
x=c.execute("SELECT * FROM user_answers WHERE user = '%s' AND answer != true_answer " % user).fetchall()
print(x)


#x=c.execute("PRAGMA table_info(user_answers)").fetchall()
#print(x)


#x=c.execute("SELECT * FROM images").fetchall()
#print(x)

