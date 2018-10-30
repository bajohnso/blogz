from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggit@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '_5y2L"F4Q8z-n-xec]/'

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
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


allowed_routes = ['index', 'login', 'signup', 'blogview', 'logout']

@app.before_request
def require_login():
    if not 'username' in session and not request.endpoint in allowed_routes: 
        return redirect('/login')


def valid_user(user):
    if len(user) < 3 or len(user) > 20:
        return False   
    elif ' ' in user:
        return False
    else: 
        return True

def valid_pw(pw):
    if len(pw) < 3 or len(pw) > 20:
        return False   
    elif ' ' in pw:
        return False
    else: 
        return True

def valid_verify(pw, verify):
    if pw == verify:
        return True
    else:
        return False

def validate_signup(username, pw, verify):
    if valid_user(username) and valid_pw(pw) and valid_verify(pw, verify):
        return True
    else:
        return False


@app.route('/blog')
def blogview():
    username = request.args.get('user')
    blog_id = request.args.get('id')
    owner = User.query.filter_by(username=username).first()
    

    if owner:
        blogs = Blog.query.filter_by(owner_id=owner.id).all()
        return render_template('blog_view.html', blogs=blogs)
    else:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('singlepost.html', blog=blog)
   

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html')

    else:
        blog_title = request.form['title']
        blog_post = request.form['post']
        owner_id = User.query.filter_by(username=session['username']).first()

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
        valid = validate_signup(username, password, verify)
        known_user = User.query.filter_by(username=username).first()
         
        if valid and not known_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('New account created.')
            return redirect('/newpost')

        elif known_user:
            flash('Username already exists.')    
            return render_template('signup.html')

        elif not valid_user(username):
            flash('Username not valid. Should be 3-20 characters w/ no spaces.')
            return render_template('signup.html')

        elif not valid_pw(password):
            flash('Password not valid. Should be 3-20 characters w/ no spaces.')
            return render_template('signup.html')

        else:
            flash("Passwords don't match.")
            return render_template('signup.html')


@app.route('/logout')
def logout():
    if not session:
        flash('Not logged in.')
        return redirect('/')
    else: 
        del session['username']
        return redirect('/')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


if __name__ == "__main__":
    app.run()   