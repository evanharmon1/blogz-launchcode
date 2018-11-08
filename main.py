from datetime import datetime
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

# App & Database Initialization
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pumpkinspice1928@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "\xff&\xf9\x87\x81g\xa4'v$\xca\xaf\xea\xc0>\xb1\xfd\xb5;K\xab\xdbw\xbc"
db = SQLAlchemy(app)


# Class for blog post with automatic datetime added at creation
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.Text)
    date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       
    def __init__(self, title, owner):
        self.title = title
        self.date = datetime.utcnow()
        self.owner = owner # user object

    def __repr__(self):
        return '<Blog %r>' % self.title 


# Class for users - relation to Blog class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username


#Get all posts unordered
def get_posts():
    return Blog.query.all()

# Get all posts ordered from newest to oldest
def get_ordered_posts():
    return Blog.query.order_by("date desc").all()

def get_users():
    return User.query.all()


@app.before_request
def require_login():
    allowed_routes = ['blog', 'index', 'login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


# Homepage
@app.route('/')
def index():
    users = get_users()
    return render_template('index.html', users=users)


# Main blog page with blog posts
@app.route('/blog', methods=['GET'])
def blog():
    id = request.args.get('id', None)
    user_id = request.args.get('user-id', None)

    if id:
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html', posts=posts)

    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', posts=posts)

    posts = get_ordered_posts()
    return render_template('blog.html', posts=posts)


# Add a new post
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    # When adding a new post from /newpost
    if request.method == 'POST':
        title = request.form.get('title', '')
        body = request.form.get('body', '')
        title_error = request.form.get('title_error', '')
        body_error = request.form.get('body_error', '')

        # Form validation for empty values
        if not title or not body:
            if title == '':
                title_error = "You left the title field blank"
            if body == '':
                body_error = "You left the body field blank"
            return redirect(f'/newpost?title={title}&body={body}&title_error={title_error}&body_error={body_error}')

        # Add new post to database
        username = session['username']
        user = User.query.filter_by(username=username).first()
        new_post = Blog(title, user)
        new_post.body = body
        db.session.add(new_post)
        db.session.commit()

        # Load the newly created post in an individual page
        id = new_post.id
        posts = Blog.query.filter_by(id=id).all()
        return render_template('blog.html', posts=posts)

    # Get request from /newpost
    title = request.args.get('title', '')
    body = request.args.get('body', '')
    title_error = request.args.get('title_error', '')
    body_error = request.args.get('body_error', '')

    return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        username_error = ''
        password_error = ''

        # Form validation for empty values
        if not username or not password:
            if username == '':
                username_error = 'You left the username field blank'
            if password == '':
                password_error = 'You left the password field blank'
            return redirect(f'/login?username={username}&username_error={username_error}&password_error={password_error}')
        
        # Check for user in database
        user = User.query.filter_by(username=username).first()
        if user:
            if password == user.password:
                session['username'] = username
                return redirect('/newpost')
        if user:
            if password != user.password:
                password_error = 'Username found, but password not correct'
                return render_template('login.html', username=username, password_error=password_error)
        else:
            username_error = 'Username not found'
            return render_template('login.html', username=username, username_error=username_error)


    username = request.args.get('username', '')
    username_error = request.args.get('username_error', '')
    password_error = request.args.get('password_error', '')

    return render_template('login.html', username=username, username_error=username_error, password_error=password_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        verify_password = request.form.get('verify_password', '')
        username_error = ''
        password_error = ''
        verify_password_error = ''
        user = User.query.filter_by(username=username).first()

        # Form validation TODO refactor into a function
        # TODO regex validation for length
        if user:
            if username == user.username:
                username_error = 'User already exists. Please choose another username'
                return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if not (3 <= len(username) <= 25):
            username_error = 'Username must be between 3 and 25 characters'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if not (3 <= len(password) <= 25):
            password_error = 'Password must be between 3 and 25 characters'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if not username or not password or not verify_password:
            if username == '':
                username_error = 'You left the username field blank'
            if password == '':
                password_error = 'You left the password field blank'
            if verify_password == '':
                verify_password_error = 'Please verify your password'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')
        if password != verify_password:
            verify_password_error = 'Your passwords do not match'
            return redirect(f'/signup?username={username}&username_error={username_error}&password_error={password_error}&verify_password_error={verify_password_error}')

        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')


    username = request.args.get('username', '')
    username_error = request.args.get('username_error', '')
    password_error = request.args.get('password_error', '')
    verify_password_error = request.args.get('verify_password_error', '')

    return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_password_error=verify_password_error)

    
if __name__ == '__main__':
    app.run()