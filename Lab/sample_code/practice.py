import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)
connect = psycopg2.connect("dbname=tutorial user=postgres password=postgres")
cur = connect.cursor()  # create cursor


cur.execute("select id from users")
res = cur.fetchone()

cur.close()
print(res)