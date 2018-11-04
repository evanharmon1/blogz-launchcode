from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

# App & Database Initialization
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
       
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Blog %r>' % self.title


def get_posts():
    return Blog.query.all()


@app.route('/blog', methods=['GET'])
def blog():

    id = request.args.get('id', None)
    if id:
        post = Blog.query.filter_by(id=id).first()
        return render_template('post.html', post=post)


    return render_template('blog.html', posts=get_posts())


@app.route('/post', methods=['POST'])
def post():
    title = request.form.get('title', '')
    body = request.form.get('body', '')
    error = request.form.get('error', '')
    if title == '' or body == '':
        error = "You left a field blank"
        return redirect(f'/newpost?title={title}&body={body}&error={error}')
    new_post = Blog(title)
    new_post.body = body
    db.session.add(new_post)
    db.session.commit()

    id = new_post.id
    posts = Blog.query.filter_by(id=id).all()
    return render_template('blog.html', posts=posts)



@app.route('/newpost', methods=['GET'])
def newpost():
    title = request.args.get('title', '')
    body = request.args.get('body', '')
    error = request.args.get('error', '')

    return render_template('newpost.html', title=title, body=body, error=error)


if __name__ == '__main__':
    app.run()