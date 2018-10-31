from flask import Flask, request, redirect, render_template, flash, session
import cgi
from app import app, db
#from flask_sqlalchemy import SQLAlchemy
from hashutils import check_pw_hash
from models import User, Blog

allowed_routes = ['index', 'login', 'signup', 'blogview', 'logout', 'all_posts']

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

def validate_signup(username, pw, verify=None):
    if valid_user(username) and valid_pw(pw) and valid_verify(pw, verify):
        return True
    else:
        return False


@app.route('/blog')
def blogview():
    username = request.args.get('user')
    blog_id = request.args.get('id')
    user = User.query.filter_by(username=username)
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

@app.route('/allposts', methods=['GET'])
def all_posts():
    
    blogs = Blog.query.all()
    owner_id = request.args.get('id')
    user =  User.query.filter_by()
    return render_template('all_posts.html', blogs=blogs)
    

@app.route('/login', methods=['GET','POST'])
def login():    
    if request.method == 'GET':
        return render_template('login.html')

    else:
        username = request.form['username']
        password = request.form['password']
        valid = validate_signup(username, password)
        user = User.query.filter_by(username=username).first()
        
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')

        elif not valid:
            flash('Username and password are incorrect.')
            return redirect('/login')
        elif user and not check_pw_hash(password, user.pw_hash):
            flash('Password is incorrect.')
            return redirect('/login')
        elif not user and check_pw_hash(password,user.pw_hash):
            flash('Username does not exist.')
            return redirect('/login' )
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

app.secret_key = '_5y2L"F4Q8z-n-xec]/'

if __name__ == "__main__":
    app.run()   