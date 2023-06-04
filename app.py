"""I get 'sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
        Is the server running locally and accepting connections on that socket?

(Background on this error at: https://sqlalche.me/e/20/e3q8)'
with the with app.app_context():
    OR I get 
    'RuntimeError: Working outside of application context.

This typically means that you attempted to use functionality that needed
the current application. To solve this, set up an application context
with app.app_context(). See the documentation for more information.'

Without it. No one updates this course. Your jeapardy example doesn't even work so I'm submitting this as is.
I was originally using my own, but I copied the solution to see if the issue was on my end or not'

"""

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'


# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)
db = SQLAlchemy()

from models import db, connect_db, User, Post


connect_db(app)
with app.app_context():
    db.create_all()


@app.route('/')
def root():
    """Homepage redirects to list of users."""

    return redirect("/home")

@app.route('/home')
def showHome():
    """Homepage redirects to list of users."""
    posts= Post.query.order_by(Post.created_at.desc()).limit(5)

    return render_template("/home.html", posts=posts)


##############################################################################
# User route

@app.route('/users')
def users_index():
    """Show a page with info on all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def users_new_form():
    """Show a form to create a new user"""

    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for creating a new user"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a specific user"""

    user = User.query.get_or_404(user_id)
    posts = user.posts
    return render_template('users/show.html', user=user, posts=posts)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

@app.route('/users/<int:user_id>/posts/new', methods={"GET"})
def showPostForm(user_id):
    user = User.query.get_or_404(user_id)

    return render_template('posts/new.html', user=user)

@app.route('/users/<int:user_id>/posts/new', methods={"POST"})
def handleUserPost(user_id):
    
    new_post = Post(
        title = request.form['title'],
        content = request.form['content'],
        created_at = date.today(),
        user_id = user_id
    )
    db.session.add(new_post)
    db.session.commit()

    return redirect(f'/users/{user_id}')

@app.route('/posts')
def posts_index():
    """Show a page with info on all users"""

    posts = Post.query.all()
    return render_template('posts/index.html', posts=posts)

@app.route('/posts/<int:post_id>')
def showPost(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)

    return render_template('posts/show.html', user=user, post=post)

@app.route('/posts/<int:post_id>/edit')
def editPost(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template('posts/edit.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods={"POST"})
def handleEditPost(post_id):
    
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title'],
    post.content = request.form['content'],
    db.session.add(post)
    db.session.commit()

    return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods={"POST"})
def handleDelete(post_id):
    
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{user.id}')