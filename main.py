from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:bloggyblog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    post = db.Column(db.String(1000))

    def __init__(self,title,post):
        self.title = title
        self.post = post

         
@app.route('/blog')
def index():
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

        if blog_title == "" or blog_post == "":
            flash('Please enter something in each field.')
            return render_template('newpost.html', post=blog_post, title=blog_title)

        else:
            new = Blog(blog_title, blog_post)
            db.session.add(new)
            db.session.commit()

            new_id = new.id
            blog = Blog.query.get(new_id)

            return render_template('singlepost.html', blog=blog)
    

if __name__ == "__main__":
    app.run()   