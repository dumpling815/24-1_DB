import psycopg2
from flask import Flask, render_template, request
import datetime

app = Flask(__name__)
connect = psycopg2.connect("dbname=term user=postgres password=postgres")
cur = connect.cursor()  # create cursor


@app.route('/')
def main():
    return render_template("login_page.html")


@app.route('/return_to_main', methods=['post'])
def re_turn_main_page():
    return render_template("main_page.html")

@app.route('/return_to_login', methods=['post'])
def re_turn_login_page():
    return render_template("login_page.html")


@app.route('/register', methods=['post'])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    if(len(id)<1 or len(password)<1):
        return render_template('log_reg_fail.html')
    
    if(send == 'sign up'):
        cur.execute("select id from users where id = '{id_}'".format(id_= id))
        if(cur.fetchone() != None):
            return render_template('ID_collision.html')
        else:
            cur.execute("insert into users values ('{id_}','{password_}')".format(id_=id,password_=password))
            connect.commit()
            return render_template("login_page.html")

    elif(send == 'login'):
        cur.execute("select id from users where id = '{id_}'".format(id_= id))
        res = cur.fetchone()
        if(res is not None and res[0] == id):
            cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by rel_date desc;")
            mov_res = cur.fetchall()

            cur.execute("select ratings,name,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id;")
            rev_res = cur.fetchall()
            return render_template("main_page.html",id = id, mov_res = mov_res, rev_res = rev_res)
        else:
            return render_template("login_fail.html")

@app.route("/mainpage", methods=['post'])
def mainpage():
    id = request.form["id"]
    mov_sort = request.form.get("mov_order",default = None)
    rev_sort = request.form.get("rev_order",default = None)
    if(mov_sort == "latest"):
        cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by rel_date desc;")
        mov_res = cur.fetchall()
        cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id\
                        order by rev_time desc;")
        rev_res = cur.fetchall()

    elif(mov_sort == "genre"):
        cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by genre;")
        mov_res = cur.fetchall()
        cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id\
                        order by rev_time desc;")
        rev_res = cur.fetchall()

    elif(mov_sort == "ratings"):
        cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by ratings;")
        mov_res = cur.fetchall()
        cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id\
                        order by rev_time desc;")
        rev_res = cur.fetchall()
    else:
        if(rev_sort == "latest"):
            cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id\
                        order by rev_time desc;")
            rev_res = cur.fetchall()
            cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by rel_date desc;")
            mov_res = cur.fetchall()
        elif(rev_sort == 'title'):
            cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id\
                        order by title;")
            rev_res = cur.fetchall()
            cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by rel_date desc;")
            mov_res = cur.fetchall()
        elif(rev_sort == 'followers'):
            cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, user_info, reviews \
                        where movies.id = reviews.mid and reviews.uid = user_info.id\
                        order by name;")
            rev_res = cur.fetchall()
            cur.execute("select distinct title,ratings,director,genre,rel_date \
                        from movies,reviews \
                        where id = mid \
                        order by rel_date desc;")
            mov_res = cur.fetchall()
    return render_template("main_page.html",id = id, mov_res = mov_res, rev_res = rev_res)


@app.route('/movie_info', methods=['post'])
def movie_info():
    id = request.form['id']
    mov_title = request.form['mov_title']
    cur.execute("select id\
                 from movies\
                 where title = '{}';".format(mov_title))
    mid = cur.fetchone()[0]
    # user_info에서 넘어온 경우.
    if(request.form.get('ratings') != None):
        cur.execute("select uid\
                    from reviews\
                    where uid = {};".format(id))
        if (id == cur.fetchone()):
            # review,rating,time 모두 update
            if(request.form.get('review_text') != None):
                cur.execute("update reviews\
                            set ratings = '{ratings}'\
                            where uid = {uid} and mid = {mid};".format(ratings=request.form.get('ratings'),uid=id,mid=mid))
                cur.execute("update reviews\
                            set review = '{review}'\
                            where uid = {uid} and mid = {mid};".format(review=request.form.get('review_text'),uid=id,mid=mid))
                time= datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                cur.execute("update reviews\
                            set rev_time = '{time}'\
                            where uid = {uid} and mid = {mid};".format(time=time,uid=id,mid=mid))
                connect.commit()
            # review가 빈칸일때.
            else:
                cur.execute("select mid\
                            from movies\
                            where title = '{mov_title}';".format(mov_title))
                mid = cur.fetchone()
                cur.execute("update reviews\
                            set ratings = '{ratings}'\
                            where uid = {uid} and mid = {mid};".format(ratings=request.form.get('ratings'),uid=id,mid=mid))
                time= datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                cur.execute("update reviews\
                            set rev_time = '{time}'\
                            where uid = {uid} and mid = {mid};".format(time=time,uid=id,mid=mid))
                connect.commit()

    cur.execute("select director, genre, rel_date\
                from movies\
                where title = '{}';".format(mov_title))
    mov_res = cur.fetchall()
    cur.execute("select ratings,name,review,rev_time\
                from reviews,user_info,movies\
                where title = '{}' and user_info.id = reviews.uid and movies.id = reviews.mid;".format(mov_title))
    rev_res = cur.fetchall()
    cur.execute("select count(review)\
                from reviews\
                where mid = '{}';".format(mid))
    rev_num = cur.fetchone()
    cur.execute("select sum(ratings)\
                from reviews\
                where mid = '{}';".format(mid))
    tot_rat = cur.fetchone()
    if rev_num[0] != 0:
        Av_rat = round(tot_rat[0] / rev_num[0],2)
    else:
        rev_num[0] = 0
    return render_template("movie_info.html",id=id,mov_title=mov_title,mov_res=mov_res,rev_res=rev_res,Av_rat = Av_rat)

@app.route("/user_info" , methods=['post'])
def user_info():
    # id: 현재 로그인 중인 유저의 id
    # user_name: 조회중인 유저 이름
    id = request.form['id']
    user_name = request.form['user_name']
    cur.execute("select id\
                from user_info\
                where name = '{}';".format(user_name))
    traverse_user_id = cur.fetchone()[0]
    cur.execute("select ratings, title, review, rev_time\
                from reviews,movies\
                where uid = '{}' and\
                mid = movies.id;".format(traverse_user_id))
    rev_res = cur.fetchall()
    cur.execute("select opid\
                from ties\
                where id = '{}' and tie = 'follow';".format(traverse_user_id))
    followers = cur.fetchall()

    if request.form.get('relation') != None:
        task = request.form['relation']
        # check if there are 'tie' between user
        cur.execute("select count(tie)\
                    from ties\
                    where id = '{id}' and opid = '{traverse_user_id}';".format(id=id,traverse_user_id=traverse_user_id))
        if cur.fetchone()[0] == 0:
            # no 'tie' between user
            cur.execute("insert into ties(id,opid,tie)\
                        values ('{id}','{opid}','{tie}');".format(id=id,opid=traverse_user_id,tie=task))
            connect.commit()
        else:
            # already exists 'tie'
            cur.execute("update ties\
                        set tie = '{tie}'\
                        where id='{id}' and opid ='{opid}';".format(tie=task,id=id,opid=traverse_user_id))
            connect.commmit()
    return render_template("user_info.html",id=id,user_name=user_name,rev_res=rev_res,followers=followers)

if __name__ == '__main__':
    app.run()
