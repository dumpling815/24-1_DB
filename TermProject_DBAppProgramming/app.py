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
    error_message = ""
    if(len(id)<1 or len(password)<1):
        error_message = "ID and password must be at least 1 character long"
        return render_template('login_page.html',error_message=error_message)
    
    if(send == 'sign up'):
        cur.execute("select id from users where id = '{id_}'".format(id_= id))
        if(cur.fetchone() != None):
            error_message = "Given ID is already exist"
            return render_template('login_page.html',error_message=error_message)
        else:
            cur.execute("insert into users values ('{id}','{password}','user')".format(id=id,password=password))
            reg_date= datetime.datetime.now().strftime("%Y-%m-%d")
            cur.execute("insert into user_info(id,reg_date) values ('{id}','{reg_date}','user')".format(id=id,reg_date=reg_date))
            connect.commit()
            return render_template("login_page.html",error_message=error_message)

    elif(send == 'login'):
        cur.execute("select id from users where id = '{}'".format(id))
        res = cur.fetchone()[0]
        cur.execute("select password from users where id ='{}';".format(id))
        pwd = cur.fetchone()[0]

        if(res is None):
            error_message = "You must register first."
            return render_template("login_page.html",error_message=error_message)
        else:
            if(pwd == password):
                cur.execute("((select title, round(avg(ratings),2) as ratings, director, genre, rel_date \
                            from movies,reviews \
                            where id = mid \
                            group by title, director, genre, rel_date)\
                            union\
                            (select title, null as ratings, director, genre, rel_date\
                            from movies\
                            where id not in (select distinct mid from reviews)))\
                            order by rel_date desc;")
                mov_res = cur.fetchall()
                cur.execute("select ratings,uid,title,review,rev_time \
                            from movies,reviews \
                            where movies.id = reviews.mid\
                                and uid not in (select opid from ties where id = '{}' and tie = 'mute')\
                            order by rev_time desc;".format(id))
                rev_res = cur.fetchall()
                return render_template("main_page.html",id = id, mov_res = mov_res, rev_res = rev_res)
            else:
                error_message = "Incorrect password."
                return render_template("login_page.html",error_message=error_message)

@app.route("/main_page", methods=['post'])
def mainpage():
    id = request.form["id"]
    # ---------------------------------------------------------------------------------
    mov_sort = request.form.get("mov_order",default = "latest")
    rev_sort = request.form.get("rev_order",default = "latest")
    if(mov_sort == "genre"):
        cur.execute("((select title, round(avg(ratings),2) as ratings, director, genre, rel_date \
                        from movies,reviews \
                        where id = mid \
                        group by title, director, genre, rel_date)\
                        union\
                        (select title, null as ratings, director, genre, rel_date\
                        from movies\
                        where id not in (select distinct mid from reviews)))\
                        order by rel_date desc;")
        mov_res = cur.fetchall()
        cur.execute("select ratings,uid,title,review,rev_time \
                        from movies,reviews \
                        where movies.id = reviews.mid\
                            and uid not in (select opid from ties where id = '{}' and tie = 'mute')\
                        order by rev_time desc;".format(id))
        rev_res = cur.fetchall()
    elif(mov_sort == "ratings"):
        cur.execute("((select title, round(avg(ratings),2) as ratings, director, genre, rel_date \
                        from movies,reviews \
                        where id = mid \
                        group by title, director, genre, rel_date)\
                        union\
                        (select title, null as ratings, director, genre, rel_date\
                        from movies\
                        where id not in (select distinct mid from reviews)))\
                        order by rel_date desc;")
        mov_res = cur.fetchall()
        cur.execute("select ratings,uid,title,review,rev_time \
                        from movies,reviews \
                        where movies.id = reviews.mid\
                            and uid not in (select opid from ties where id = '{}' and tie = 'mute')\
                        order by rev_time desc;".format(id))
        rev_res = cur.fetchall()
    elif(mov_sort == 'latest'): #mov_sort == 'latest'
        if(rev_sort == "latest"):
            cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, reviews \
                        where movies.id = reviews.mid\
                            and uid not in (select opid from ties where id = '{}' and tie = 'mute')\
                        order by rev_time desc;".format(id))
            rev_res = cur.fetchall()
            cur.execute("((select title, round(avg(ratings),2) as ratings, director, genre, rel_date \
                        from movies,reviews \
                        where id = mid \
                        group by title, director, genre, rel_date)\
                        union\
                        (select title, null as ratings, director, genre, rel_date\
                        from movies\
                        where id not in (select distinct mid from reviews)))\
                        order by rel_date desc;")
            mov_res = cur.fetchall()
        elif(rev_sort == 'title'):
            cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, reviews \
                        where movies.id = reviews.mid\
                            and uid not in (select opid from ties where id = '{}' and tie = 'mute')\
                        order by title;".format(id))
            rev_res = cur.fetchall()
            cur.execute("((select title, round(avg(ratings),2) as ratings, director, genre, rel_date \
                        from movies,reviews \
                        where id = mid \
                        group by title, director, genre, rel_date)\
                        union\
                        (select title, null as ratings, director, genre, rel_date\
                        from movies\
                        where id not in (select distinct mid from reviews)))\
                        order by rel_date desc;")
            mov_res = cur.fetchall()
        else: #(rev_sort == 'followers'):
            cur.execute("select ratings,uid,title,review,rev_time \
                        from movies, reviews \
                        where movies.id = reviews.mid\
                            and uid in (select opid from ties where id = '{}' and tie = 'follow')\
                        order by uid;".format(id))
            rev_res = cur.fetchall()
            cur.execute("((select title, round(avg(ratings),2) as ratings, director, genre, rel_date \
                        from movies,reviews \
                        where id = mid \
                        group by title, director, genre, rel_date)\
                        union\
                        (select title, null as ratings, director, genre, rel_date\
                        from movies\
                        where id not in (select distinct mid from reviews)))\
                        order by rel_date desc;")
            mov_res = cur.fetchall()
    # ---------------------------------------------------------------------------------    
    return render_template("main_page.html",id = id, mov_res = mov_res, rev_res = rev_res)

@app.route('/movie_info', methods=['post'])
def movie_info():
    id = request.form['id']
    mov_title = request.form['mov_title']
    cur.execute("select id\
                 from movies\
                 where title = '{}';".format(mov_title))
    mid = cur.fetchone()[0]

        # movie_info.html에서 review submit 한 경우.
    if(request.form.get('review_text') != None):
        rev_time= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ratings=request.form.get('ratings')
        review=request.form.get('review_text')
        cur.execute("select count(review)\
                    from reviews\
                    where mid = '{mid}' and uid ='{id}';".format(mid=mid,id=id))
        exists = cur.fetchone()[0]
        if (exists == 0):
            cur.execute("insert into reviews\
                        values('{mid}','{uid}','{ratings}','{review}','{rev_time}');".format(mid=mid,uid=id,ratings=ratings,review=review,rev_time=rev_time))
        else:
            cur.execute("update reviews\
                        set ratings = '{ratings}'\
                        where uid = '{uid}' and mid = '{mid}';".format(ratings=request.form.get('ratings'),uid=id,mid=mid))
            cur.execute("update reviews\
                        set review = '{review}'\
                        where uid = '{uid}' and mid = '{mid}';".format(review=request.form.get('review_text'),uid=id,mid=mid))
            cur.execute("update reviews\
                        set rev_time = '{time}'\
                        where uid = '{uid}' and mid = '{mid}';".format(time=rev_time,uid=id,mid=mid))
        connect.commit()
        cur.execute("select director, genre, rel_date\
                from movies\
                where title = '{}';".format(mov_title))
        mov_res = cur.fetchall()
        cur.execute("select ratings,uid,review,rev_time\
                    from reviews\
                    where mid = '{mid}'\
                        and uid not in (select opid from ties where id = '{id}' and tie = 'mute')\
                    order by rev_time desc;".format(mid=mid,id=id))
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
    # ---------------------------------------------------------------------------------
    cur.execute("select director, genre, rel_date\
                from movies\
                where title = '{}';".format(mov_title))
    mov_res = cur.fetchall()
    cur.execute("select ratings,uid,review,rev_time\
                from reviews\
                where mid = '{}'\
                    and uid not in (select opid from ties where id = '{}' and tie = 'mute');".format(mid,id))
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
        return render_template("movie_info.html",id=id,mov_title=mov_title,mov_res=mov_res,rev_res=rev_res,Av_rat = 'None')
    return render_template("movie_info.html",id=id,mov_title=mov_title,mov_res=mov_res,rev_res=rev_res,Av_rat = Av_rat)

@app.route("/user_info" , methods=['post'])
def user_info():
    # id: 현재 로그인 중인 유저의 id
    # user_id: 조회중인 유저 id
    id = request.form['id']
    user_id = request.form['user_id']
    cur.execute("select role from users where id='{}';".format(id))
    role = cur.fetchone()[0]

    # Follwing, Muting process --------------------
    if request.form.get('relation') != None:
        task = request.form['relation']
        # check if there are 'tie' between user
        cur.execute("select count(tie)\
                    from ties\
                    where id = '{id}' and opid = '{user_id}';".format(id=id,user_id=user_id))
        if cur.fetchone()[0] == 0:
            # no 'tie' between user
            cur.execute("insert into ties(id,opid,tie)\
                        values ('{id}','{opid}','{tie}');".format(id=id,opid=user_id,tie=task))
            connect.commit()
        else:
            # already exists 'tie'
            cur.execute("update ties\
                        set tie = '{tie}'\
                        where id='{id}' and opid ='{opid}';".format(tie=task,id=id,opid=user_id))
            connect.commit()
    #--------------------------------------------
    cur.execute("select ratings, title, review, rev_time\
                from reviews,movies\
                where uid = '{}' and\
                mid = movies.id;".format(user_id))
    rev_res = cur.fetchall()
    cur.execute("select id\
                from ties\
                where opid = '{}' and tie = 'follow';".format(user_id))
    followers = cur.fetchall()
    if role == 'admin':
        if id == user_id: #admin 이 자기 페이지 보는것.
            cur.execute("select ratings, title, review, uid\
                        from reviews,movies\
                        where id = mid;")
            ent_rev = cur.fetchall()
            cur.execute("select id, name, email, reg_date\
                from user_info;")
            ent_user = cur.fetchall()
            return render_template("/admin_page.html",id=id,rev_res=rev_res,ent_rev=ent_rev,ent_user=ent_user)
        else:  #admin이 다른 사용자 보는것.
            return render_template("/user_info.html",id=id,user_id=user_id,rev_res=rev_res,followers=followers)
    else: # not admin
        if id == user_id:
            cur.execute("select opid\
                    from ties\
                    where id = '{}' and tie = 'follow';".format(id))
            followed_res = cur.fetchall()
            cur.execute("select opid\
                        from ties\
                        where id = '{}' and tie = 'mute';".format(id))
            muted_res = cur.fetchall()
            return render_template("/my_info.html",id=id,rev_res=rev_res,followers=followers,followed_res=followed_res,muted_res=muted_res)
        else:
            cur.execute("select role from users where id='{}';".format(user_id))
            target_role = cur.fetchone()[0]
            if target_role == 'admin':
                return render_template("/admin_info.html",id=id,user_id=user_id,rev_res=rev_res)
            else:
                return render_template("/user_info.html",id=id,user_id=user_id,rev_res=rev_res,followers=followers)

@app.route("/my_info", methods=['post'])
def my_info():
    id = request.form['id']

    #Tie fixing -----------------------------------------------
    if request.form.get('cancel') != None:
        task = request.form['cancel']
        task = task[2:]
        who = request.form['who']
        cur.execute("delete from ties\
                    where id = '{id}' and opid = '{who}'\
                    and tie = '{task}';".format(id=id,who=who,task=task))
        connect.commit()
    #----------------------------------------------------------
    cur.execute("select ratings, title, review, rev_time\
                from reviews,movies\
                where uid = '{}' and\
                mid = movies.id;".format(id))
    rev_res = cur.fetchall()
    cur.execute("select id\
                from ties\
                where opid = '{}' and tie = 'follow';".format(id))
    followers = cur.fetchall()    
    cur.execute("select opid\
                from ties\
                where id = '{}' and tie = 'follow';".format(id))
    followed_res = cur.fetchall()
    cur.execute("select opid\
                from ties\
                where id = '{}' and tie = 'mute';".format(id))
    muted_res = cur.fetchall()

    return render_template("my_info.html",id=id,rev_res=rev_res,followers=followers,followed_res=followed_res,muted_res=muted_res)

@app.route("/admin_page", methods=['post'])
def admin_page():
    id = request.form['id']
    if request.form.get('add') != None:
        mov_title = request.form['mov_title']
        director = request.form['director']
        genre = request.form['genre']
        rel_date = request.form['rel_date']

        cur.execute("select count(id) from movies;")
        new_mid = cur.fetchone()[0] +1
        cur.execute("insert into movies(id,title,director,genre,rel_date)\
                        values('{id}','{title}','{director}','{genre}','{rel_date}');"\
                    .format(id=new_mid,title=mov_title,director=director,genre=genre,rel_date=rel_date))
        connect.commit()

    if request.form.get('delete_rev') != None:
        mov_title = request.form['delete_title']
        uid = request.form['delete_uid']
        cur.execute("select id from movies where title='{}';".format(mov_title))
        mid = cur.fetchone()[0]
        cur.execute("delete from reviews\
                    where uid = '{}' and mid = '{}';".format(uid,mid))
        connect.commit()

    if request.form.get('delete_user') != None:
        delete_id = request.form['delete_id']
        cur.execute("delete from reviews\
                    where uid = '{}';".format(delete_id))
        cur.execute("delete from mal_user\
                    where id = '{}';".format(delete_id))
        cur.execute("delete from ties\
                    where id = '{}';".format(delete_id))
        cur.execute("delete from ties\
                    where opid = '{}';".format(delete_id))
        cur.execute("delete from user_info\
                    where id = '{}';".format(delete_id))
        cur.execute("delete from users\
                    where id = '{}';".format(delete_id))
        connect.commit()

    cur.execute("select ratings, title, review, rev_time\
                from reviews,movies\
                where uid = '{}' and\
                mid = movies.id;".format(id))
    rev_res = cur.fetchall()

    cur.execute("select ratings, title, review, uid\
                from reviews,movies\
                where id = mid;")
    ent_rev = cur.fetchall()

    cur.execute("select id, name, email, reg_date\
                from user_info;")
    ent_user = cur.fetchall()

    return render_template("admin_page.html",id=id,rev_res=rev_res,ent_rev=ent_rev,ent_user=ent_user)
if __name__ == '__main__':
    app.run()
