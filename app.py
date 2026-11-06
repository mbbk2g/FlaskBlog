import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

# function to retreive post from db
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)

    return post

# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    # get a connection to the db
    conn = get_db_connection()

    # execute query to read all posts from posts table in db
    posts = conn.execute('SELECT * FROM posts').fetchall()

    # close connection
    conn.close()

    # send posts to index.html template to display
    return render_template('index.html', posts=posts)

# route to create a post
@app.route('/create/', methods=('GET', 'POST'))
def create():
    # determine if page is being requested with GET or POST
    if request.method == 'POST':
        # get title and content
        title = request.form['title']
        content = request.form['content']

        # if user did not submit title or content, display error
        if not title:
            flash('Title is required')
        elif not content:
            flash('Content is required')
        # else, make db connection and insert new content
        else:
            conn = get_db_connection()
            #insert data into db
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

# create a route to edit a post, load the page with GET or POST method
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
# pass the post id as url parameter
def edit(id):
    # get post from db with select query for post with flask id
    post = get_post(id)

    # determine if page was requested with GET or POST
    # if POST process form data. Get and validate date then redirect to homepage
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # if not title then flash error
        if not title:
            flash('Title is required')
        elif not content:
            flash('Content is required')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()

            # redirect to homepage
            return redirect(url_for('index'))

    # if GET then display page
    return render_template('edit.html', post=post)

# create a route to delete a post
# delete route will only work with POST method
# post id will be url parameter
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    # get post
    post = get_post(id)

    # connect to db
    conn = get_db_connection()

    # execute delete query
    conn.execute('DELETE from posts WHERE id = ?', (id,))

    # commit and close
    conn.commit()
    conn.close()

    # flash success message
    flash('"{}" was successfully deleted'.format(post['title']))

    # redirect to homepage
    return redirect(url_for('index'))

app.run(port=5002)