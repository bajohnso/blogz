from flask import Flask, request, redirect, render_template
#from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
#app.config['SQLALCHEMY_ECHO'] = True
#db = SQLAlchemy(app)


@app.route('/blog', methods=['GET'])
def main_blog():
    return render_template('blog.html')