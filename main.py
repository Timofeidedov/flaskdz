from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import sqlite3

list_of_questions=[("1) Я часто проявляю в жизни слабость, в чем порой раскаиваюсь",), ("2) Я готов понять человека, проявляющего слабость",),("3) Я готов простить человека, проявляющего слабость",), ("4) От слабых людей всегда больше зла, чем от сильных",),
                   ("5) Меня привлекают сильные люди",), ("6) Мне симпатичны физически сильные люди",), ("7) Люди, у которых нет слабостей, кажутся мне странными или отталкивают меня",),
                   ("8) Я считаю излишнее проявление эмоций слабостью",),("9) Я считаю себя сильным человеком",),("10) Что для вас (в первую очередь) проявление слабости?",),("11) Что способно помочь вам преодолеть слабость?",),("Фидбэк",)]

db = sqlite3.connect(r'test.db')
cur = db.cursor()
cur.execute(
    """CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    q1 INTEGER,
    q2 INTEGER,
    q3 INTEGER,
    q4 INTEGER,
    q5 INTEGER,
    q6 INTEGER,
    q7 INTEGER,
    q8 INTEGER,
    q9 INTEGER,
    q10 TEXT,
    q11 TEXT,
    q12 TEXT)
    """)

cur.execute(
    """CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
    )""")

cur.execute(
    """CREATE TABLE 
    user ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT,
    education TEXT,
    age INTEGER )""")
for smth in list_of_questions:
    a=smth
    cur.execute(
        '''INSERT into questions (text) VALUES (?)''',a
    )
db.commit()
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Integer)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)


class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)
    q4 = db.Column(db.Integer)
    q5 = db.Column(db.Integer)
    q6 = db.Column(db.Integer)
    q7 = db.Column(db.Integer)
    q8 = db.Column(db.Integer)
    q9 = db.Column(db.Integer)
    q10 = db.Column(db.Text)
    q11 = db.Column(db.Text)
    q12 = db.Column(db.Text)

@app.route('/')
def base():
    with open("myresearch.txt", "r", encoding='utf-8') as f:
        content = f.read().split('\n')
    return render_template("base.html", content=content)
@app.route('/questions')
def question_page():
    questions = Questions.query.all()[:-3]
    return render_template(
        'questions.html',
        questions=questions
    )

@app.route('/process', methods=['get'])
def answer_process():
    # если нет ответов, то отсылаем решать анкету
    if not request.args:
        return redirect(url_for('question_page'))

    # достаем параметры
    gender = request.args.get('gender')
    education = request.args.get('education')
    age = request.args.get('age')

    # создаем профиль пользователя
    user = User(
        age=age,
        gender=gender,
        education=education
    )
    # добавляем в базу
    db.session.add(user)
    # сохраняемся
    db.session.commit()
    # получаем юзера с айди (автоинкремент)
    db.session.refresh(user)

    # получаем два ответа
    q1 = request.args.get('q1')
    q2 = request.args.get('q2')
    q3 = request.args.get('q3')
    q4 = request.args.get('q4')
    q5 = request.args.get('q5')
    q6 = request.args.get('q6')
    q7 = request.args.get('q7')
    q8 = request.args.get('q8')
    q9 = request.args.get('q9')
    q10 = request.args.get('q10')
    q11 = request.args.get('q11')
    q12 = request.args.get('q12')


    # привязываем к пользователю (см. модели в проекте)
    answer = Answers(id=user.id, q1=q1, q2=q2, q3=q3, q4=q4, q5=q5,q6=q6,q7=q7,q8=q9,q9=q9,q10=q10,q11=q11,q12=q12)
    # добавляем ответ в базу
    db.session.add(answer)
    # сохраняемся
    db.session.commit()

    return 'Спасибо за ответы! Теперь вы (при желании) можете вернуться на главную и посмотреть на статистику'
@app.route('/stats')
def stats():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = age_stats[0]
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['total_count'] = User.query.count()
    all_info['q2_mean'] = db.session.query(func.avg(Answers.q2)).one()[0]
    all_info['q3_mean'] = db.session.query(func.avg(Answers.q3)).one()[0]
    all_info['q5_mean'] = db.session.query(func.avg(Answers.q2)).one()[0]
    all_info['q7_mean'] = db.session.query(func.avg(Answers.q3)).one()[0]
    if all_info['q2_mean']//1==1:
        content1='не согласен'
    elif all_info['q2_mean']//1==2:
        content1='скорее нет'
    elif all_info['q2_mean']//1==3:
        content1='затрудняюсь'
    elif all_info['q2_mean']//1==4:
        content1='скорее да'
    elif all_info['q2_mean']//1==5:
        content1='согласен'
    if all_info['q3_mean']//1==1:
        content2='не согласен'
    elif all_info['q3_mean']//1==2:
        content2='скорее нет'
    elif all_info['q3_mean']//1==3:
        content2='затрудняюсь'
    elif all_info['q3_mean']//1==4:
        content2='скорее да'
    elif all_info['q3_mean']//1==5:
        content2='согласен'
    if all_info['q5_mean']//1==1:
        content3='не согласен'
    elif all_info['q5_mean']//1==2:
        content3='скорее нет'
    elif all_info['q5_mean']//1==3:
        content3='затрудняюсь'
    elif all_info['q5_mean']//1==4:
        content3='скорее да'
    elif all_info['q5_mean']//1==5:
        content3='согласен'
    if all_info['q7_mean']//1==1:
        content4='не согласен'
    elif all_info['q7_mean']//1==2:
        content3='скорее нет'
    elif all_info['q7_mean']//1==3:
        content4='затрудняюсь'
    elif all_info['q7_mean']//1==4:
        content4='скорее да'
    elif all_info['q7_mean']//1==5:
        content4='согласен'
    return render_template('results.html', all_info=all_info,content1=content1,content2=content2, content3=content3, content4=content4)
if __name__ == '__main__':
    app.run()