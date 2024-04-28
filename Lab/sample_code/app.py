import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)
connect = psycopg2.connect("dbname=tutorial user=postgres password=postgres")
cur = connect.cursor()  # create cursor


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/return', methods=['post'])
def re_turn():
    return render_template("main.html")


@app.route('/print_table', methods=['post'])
def print_table():
    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()

    return render_template("print_table.html", users=result)


@app.route('/register', methods=['post'])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    if(send == 'sign up'):
        cur.execute("select id from users where id = '{id_}'".format(id_= id))
        if(cur.fetchone() != None):
            return render_template('ID_collision.html')
        else:
            cur.execute("insert into users values ('{id_}','{password_}')".format(id_=id,password_=password))
            connect.commit()
            return render_template("main.html")

    elif(send == 'login'):
        cur.execute("select id from users where id = '{id_}'".format(id_= id))
        res = cur.fetchone()
        if(res is not None and res[0] == id):
            return render_template("login_success.html")
        else:
            return render_template("login_fail.html")

# cur.close()
if __name__ == '__main__':
    app.run()
