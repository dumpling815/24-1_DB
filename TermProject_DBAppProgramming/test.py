import psycopg2
from flask import Flask, render_template, request
import datetime

app = Flask(__name__)
connect = psycopg2.connect("dbname=term user=postgres password=postgres")
cur = connect.cursor()  # create cursor


cur.execute("((select title, avg(ratings) as ratings, director, genre, rel_date \
                from movies,reviews \
                where id = mid \
                group by title, director, genre, rel_date)\
                union\
                (select title, null as ratings, director, genre, rel_date\                    from movies\
                where id not in (select distinct mid from reviews)))\
                    order by rel_date desc;")
mov_res = cur.fetchall()
# if(mov_res[1] == -1):
#     mov_res[1] = 'None'
# else:
#     mov_res[1] = round(float(mov_res[1][1]),2)

print(mov_res)