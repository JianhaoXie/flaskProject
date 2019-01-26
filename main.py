# encoding: utf-8

from flask import Flask,render_template,request,redirect,session,url_for,g
from sqlalchemy import or_
import config
from models import User,Question,Answer
from exts import db
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

@app.route('/')
def index():
    content = {
        'questions' : Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**content)

@app.route('/login/', methods=["GET","POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get("telephone")
        password = request.form.get("password")
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 如果想在31天内都不需要登录
            session.permanent = True
            return redirect(url_for("index"))
        else:
            return "手机号或者密码输入错误,请确定后再登录!"



@app.route('/regist/', methods=["GET","POST"])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get("telephone")
        username = request.form.get("username")
        # print(type(username))
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # 手机号验证, 如果手机号注册了,就不能再注册了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return "该手机号码已经被注册,请更换手机号码"
        else:
            # password1 要跟 password2 相等才可以
            if password1 != password2:
                return '两次密码不相等,请核对后再填写'
            else:
                user = User(telephone=telephone,username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


@app.route("/logout/")
def logout():
    # 三种方式清除session
    session.pop('user_id')
    # del session['user_id']
    # session.clear()
    return redirect(url_for('login'))

@app.route('/question/',methods=["GET", "POST"])
@login_required
def question():
    if request.method == "GET":
        return render_template("question.html")
    else:
        title = request.form.get("title")
        content = request.form.get("content")
        question = Question(title=title,content=content)
        # user_id = session.get("user_id")
        # user = User.query.filter(User.id == user_id).first()
        # question.author = user

        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for("index"))

@app.route("/detail/<question_id>/")
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    answer_num = len(question_model.answers)
    return render_template("detail.html",question=question_model,answer_num=answer_num)


@app.route('/add_answer/', methods=["POST"])
@login_required
def add_answer():
    content = request.form.get('answer-content')
    question_id = request.form.get('question_id')

    answer = Answer(content=content)
    # user_id = session['user_id']
    # user = User.query.filter(User.id == user_id).first()
    # answer.author = user
    answer.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for("detail",question_id=question_id))


@app.route('/search/')
def search():
    q = request.args.get('q')
    # 差早内容要么在title,要么在content
    # 或的方式
    questions = Question.query.filter(or_(Question.title.contains(q),
                Question.content.contains(q))).order_by('-create_time')
    return render_template('index.html',questions=questions)

# 每次请求之前都会先执行的钩子函数
@app.before_request
def my_before_request():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        g.user = user


# 上下文处理器
@app.context_processor
def my_context_processor():
    # user_id = session.get("user_id")
    # if user_id:
    #     user = User.query.filter(User.id == user_id).first()
    #     if user:
    #         return {'user':user}
    if hasattr(g,'user'):
        return {'user':g.user}
    return {}

if __name__ == '__main__':
    app.run()
