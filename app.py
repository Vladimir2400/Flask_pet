from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test2.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.id


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
            return redirect('/posts')
        except:
            return "При добавлении статьи произошла ошибка"

    else:
        return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True)
