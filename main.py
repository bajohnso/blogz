from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggit@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    post = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,post,owner):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    pw_hash = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    query = request.args.get('username')
    if not query:    
        users = User.query.all()
        return render_template('index.html', users=users)
    else:
        blogs = Blog.query.filter_by(owner_id=id).first()
        return render_template('blog.html', blogs=blogs)

        
@app.route('/blog')
def blog():
    query = request.args.get('id')
    
    if not query:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)

    else:
        blog = Blog.query.filter_by(id=query).first()
        return render_template('singlepost.html', blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    else:
        blog_title = request.form['title']
        blog_post = request.form['post']
        owner_id = User.id
        if blog_title == "" or blog_post == "":
            flash('Please enter something in each field.')
            return render_template('newpost.html', post=blog_post, title=blog_title)

        else:
            new = Blog(blog_title, blog_post, owner_id)
            db.session.add(new)
            db.session.commit()

            new_id = new.id
            blog = Blog.query.get(new_id)

            return render_template('singlepost.html', blog=blog)

@app.route('/login', methods=['GET','POST'])
def login():    
    if request.method == 'GET':
        return render_template('login.html')
    
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        elif user and not check_pw_hash(password, user.pw_hash):
            flash('Password is incorrect.')
            return redirect('/login')
        elif not user and check_pw_hash(password,user.pw_hash):
            flash('Username does not exist.')
            return redirect('/login')
        else:
            flash('Username and password are incorrect.')
            return redirect('/login')

@app.route('/signup', methods=['GET','POST'])
def signup():   
    if request.method == 'GET':
        return render_template('signup.html')
    
    else:
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # VERIFY INPUTS.

        known_user = User.query.filter_by(username=username).first()

        if not known_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            #flash('New account created.')
            return redirect('/newpost')
        else:
            return ('Username already exists.')

@app.route('/logout')
def logout():
    if not session:
        return ('Not logged in.')
    else: 
        del session['username']
        return redirect('/blog')



if __name__ == "__main__":
    app.run()   