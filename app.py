from flask import Flask, render_template, request, redirect, flash, session, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from datetime import datetime

from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash

from UserLogin import UserLogin

app = Flask(__name__)
# login_manager = LoginManager(app)
app.config['SECRET_KEY'] = '8c90b4c5696261fe207bd2755d1787686d2ffb3a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# @login_manager.user_loader
# def load_user(user_id):
#     print('load_user')
#     return UserLogin().fromDB(user_id, db)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    pr = db.relationship('Profile', backref='user', uselist=False)

    # @staticmethod
    # def getUsers(user_id):
    #     try:
    #         res = Users.query.get(user_id)
    #         if not res:
    #             print('Пользователь не найден')
    #             return False
    #
    #         return res
    #     except OperationalError as e:
    #         print('Ошибка при работе с базой данных'+str(e))
    #
    #     return False


    def __repr__(self):
        return f'<users {self.id}>'


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts')
def posts():
    post = Post.query.all()
    return render_template('posts.html', posts=post)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        post = Post(title=title, intro=intro, text=text)
        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/index')
        except:
            return "При добавлении статьи произошла ошибка"

    return render_template('create.html')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')

    return render_template('contact.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        try:
            hash = generate_password_hash(request.form['password'])
            user = Users(email=request.form['email'], password=hash)
            db.session.add(user)
            db.session.flush()

            profile = Profile(name=request.form['name'], old=request.form['old'],
                              city=request.form['city'], user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as ex:
            db.session.rollback()
            print(f'Произошла ошибка при регистрации: {ex}')
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        # if user and check_password_hash(user.password, password):
        #     userlogin = UserLogin().create(user)
        #     login_user(userlogin)
        #     return redirect(url_for('posts'))
        # else:
        #     flash('Неправильный логин или пароль')

    return render_template('login.html')


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template('profile.html', username=username)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
