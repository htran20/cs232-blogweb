"""
General API Description
This API provides access to a database of accounts, blogs, comments.

Supported requests

GET /api/accounts/

Description:
Get a list of all accounts

Parameters:
None

Example response:
[
  {
    "id": 1,
    "username": "htran20"
  },
  {
    "id": 2,
    "username": "tdinh20"
  }
]

GET /api/accounts/:account_id

Description:
Get a single account by ID

Parameters:
account_id - the ID of the account

Example response:
{
    "id": 1,
    "username": "htran20"
}

POST /api/accounts/

Description:
Create a new accounts with username, password provided

Parameters:
None

Example response:
{
    "id": 1,
    "username": "htran20"
}

PATCH /api/accounts/:account_id

Description:
Modify the account's password with new password provided

Parameters:
account_id - the ID of the account

Example response:
{
    "id": 1,
    "username": "htran20"
}

DELETE /api/accounts/:account_id

Description:
Delete an account

Parameters:
id - the ID of the account

Example response:
{
  "Delete Successfully"
}

GET /api/blogs/

Description:
Get all blogs

Parameters:
None

Example response:
[
  {
    "author_id": 1,
    "content": "What do you want to say?",
    "id": 1,
    "time": "Mon Apr 30 00:21:19 2018",
    "title": "Hello World"
  },
  {
    "author_id": 2,
    "content": "What do you want to say?What do you want to say?",
    "id": 2,
    "time": "Mon Apr 30 00:31:54 2018",
    "title": "ashjashjawhdjas"
  }
]

GET /api/blogs/:blog_id

Description:
Get a single blog by ID

Parameters:
blog_id - the ID of the blog

Example response:
{
    "author_id": 1,
    "content": "What do you want to say?",
    "id": 1,
    "time": "Mon Apr 30 00:21:19 2018",
    "title": "Hello World"
}

POST /api/blogs/

Description:
Create a new blog with author_id, content, title provided

Parameters:
None

Example response:
{
    "author_id": 1,
    "content": "What do you want to say?",
    "id": 1,
    "time": "Mon Apr 30 00:21:19 2018",
    "title": "Hello World"
}

PATCH /api/blogs/:blog_id

Description:
Modify a blog with at least new content or new title provided

Parameters:
blog_id - the ID of the blog

Example response:
{
    "author_id": 1,
    "content": "Hello, how are you?",
    "id": 1,
    "time": "Mon Apr 30 00:21:19 2018",
    "title": "Hello World"
}

DELETE /api/blogs/:blog_id

Description:
Delete a blog

Parameters:
id - the ID of the blog

Example response:
{
  "Delete Successfully"
}

GET /api/comments/

Description:
Get all comments

Parameters:
None

Example response:
[
  {
    "author_id": 1,
    "blog_id": 1,
    "content": "LOL",
    "id": 1,
    "time": "Mon Apr 30 00:21:30 2018"
  },
  {
    "author_id": 1,
    "blog_id": 1,
    "content": "wonderful",
    "id": 2,
    "time": "Mon Apr 30 00:21:38 2018"
  }
]

GET /api/comments/:comment_id

Description:
Get a single comment by ID

Parameters:
comment_id - the ID of the comment

Example response:
{
    "author_id": 1,
    "blog_id": 1,
    "content": "LOL",
    "id": 1,
    "time": "Mon Apr 30 00:21:30 2018"
}

POST /api/accounts/

Description:
Create a new account with author_id, content, blog_id provided

Parameters:
None

Example response:
{
    "author_id": 1,
    "blog_id": 1,
    "content": "LOL",
    "id": 1,
    "time": "Mon Apr 30 00:21:30 2018"
}

PATCH /api/comments/:comment_id

Description:
Modify a comment with new content provided

Parameters:
comment_id - the ID of the comment

Example response:
{
    "author_id": 1,
    "content": "Hello, how are you?",
    "id": 1,
    "time": "Mon Apr 30 00:21:19 2018",
    "title": "Hello World"
}

DELETE /api/comments/:comment_id

Description:
Delete a comment

Parameters:
id - the ID of the comment

Example response:
{
  "Delete Successfully"
}
"""
import hashlib
import os
import sys
import requests
from functools import wraps
from flask import Flask, g, jsonify, request, render_template,\
    redirect
from flask_login import LoginManager, UserMixin, login_user,\
    logout_user, current_user, login_required
from flask.views import MethodView
from blogdb import BlogDB

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['DATABASE'] = os.path.join(app.root_path, 'blog.sqlite')
app.config["SECRET_KEY"] = 'hello'
app.config.update(
    DATABASE=os.path.join(app.root_path, 'WooMessages.sqlite'),
    DEBUG=True,
    SECRET_KEY='hello'
)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.cli.command('initdb')
def initdb_command():
    """
    Implements blog database initialization
    :return: prints statement confirming initialization of database
    """
    BlogDB(app.config['DATABASE']).init_db()

    print('Initialized the blog database.')


def get_db():
    """
    Connects to the database. If a connection has already been created,
    the existing connection is used, otherwise it creates a new connection.
    :return: BlogDB object representing the database
    """

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = BlogDB(app.config['DATABASE'])
        g.sqlite_db.connect_db()

    return g.sqlite_db


def verify_account_by_id(id):
    """
    Prompts users for the username and password. Checks the username and
    password against the existing account in the database. Used for requests
    which associated with a specific account (like POST, DELETE, PATCH).

    :param id: ID of the account to verify
    :return: none
    """

    db = get_db()
    print('Log in: ')
    username = input('Username: ')
    password = input('Password: ')

    account = db.query_by_id('account', id)

    if account is None:
        raise RequestError(404, 'Account not found')

    if username != account['username']:
        raise RequestError(401, 'Username not found')

    salt = '7jk'
    hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

    if hashed_password != account['password']:
        raise RequestError(401, 'Invalid authentication')


def log_in():
    """
    Prompts users for the username and password. Checks if the account exists
    in the database and verifies the password. Used for generic requests by
    any account (like GET).

    :return: ID of the account
    """

    db = get_db()
    print('Log in: ')
    username = input('Username: ')
    password = input('Password: ')
    account = db.get_account_by_username(username)

    if account is None:
        raise RequestError(401, 'Username not found')

    salt = '7jk'
    hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

    if hashed_password != account['password']:
        raise RequestError(401, 'Invalid authentication')

    return account['id']


def browser_log_in(username, password):
    """
    Checks if the username and password matches an existing account in the
    database. Used for logging in on the browser.

    :param username: username of the account
    :param password: password of the account
    :return:
    """

    db = get_db()
    account = db.get_account_by_username(username)

    if account is None:
        raise RequestError(401, 'Username not found 1')

    salt = '7jk'
    hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

    if hashed_password != account['password']:
        raise RequestError(401, 'Invalid authentication')


class RequestError(Exception):
    """
    This custom exception class is for easily handling errors in requests,
    such as when the user provides an ID that does not exist or omits a
    required field.
    """

    def __init__(self, status_code, error_message):
        Exception.__init__(self)

        self.status_code = str(status_code)
        self.error_message = error_message

    def to_response(self):
        """
        Create a Response object containing the error message as JSON.
        :return: the response
        """

        response = jsonify({'error': self.error_message})
        response.status = self.status_code
        return response


@app.errorhandler(RequestError)
def handle_invalid_usage(error):
    """
    Returns a JSON response built from a RequestError.
    :param error: the RequestError
    :return: a response containing the error message
    """
    return error.to_response()


class BlogsView(MethodView):
    """
    This view handles all the /api / blogs / requests.
    """

    def get(self, blog_id):
        """
        Returns JSON representing all of the blogs if blog_id is None,
        or a single blog if blog_id is not None.

        :param blog_id: id of a blog, or None for all blogs
        :return: JSON response
        """

        db = get_db()
        if db.get_all_accounts() == []:
            response = jsonify([])
        else:
            log_in()
            if blog_id is None:
                response = jsonify(db.get_all_rows('blog'))
            else:
                blog = db.query_by_id('blog', blog_id)

                if blog is not None:

                    response = jsonify(blog)
                else:
                    raise RequestError(404, 'blog not found')

        return response

    def post(self):
        """
        Handles a POST request to insert a new blog. Returns a JSON
        response representing the new blog.
        The blog's title, content, author_id must be provided in the
        requests's form data.
        :return: a response containing the JSON representation of the blog
        """

        db = get_db()
        if 'title' not in request.form:
            raise RequestError(422, 'blog title required')
        elif 'content' not in request.form:
            raise RequestError(422, 'blog content required')
        elif 'author_id' not in request.form:
            raise RequestError(422, 'author id required')
        else:
            verify_account_by_id(request.form['author_id'])
            insert = db.insert_blog(request.form['title'],
                                    request.form['content'],
                                    request.form['author_id'])
            response = jsonify(insert)

        return response

    def delete(self, blog_id):
        """
        Handle DELETE requests. id must be provided

        :param blog_id: id of a blog
        :return: JSON response
        """

        db = get_db()
        blog = db.query_by_id('blog', blog_id)

        if blog is not None:
            verify_account_by_id(blog['author_id'])
            db.delete_blog(blog_id)
            response = jsonify("Delete Successfully")
        else:
            raise RequestError(404, 'Blog id not found')

        return response

    def patch(self, blog_id):
        """
        Handles a PATCH request to update a blog. Returns a JSON
        response representing the updated blog.

        At least new title or content must be provided in the
        requests's form data.

        :param blog_id: id of a blog
        :return: a response containing the JSON representation of the
        updated blog
        """

        db = get_db()
        content = None
        title = None

        if 'content' in request.form:
            content = request.form['content']
        if 'title' in request.form:
            title = request.form['title']
        if title is None and content is None:
            raise RequestError(422, 'At least new title or content'
                                    ' must be provided')

        blog = db.query_by_id('blog', blog_id)

        if blog is None:
            raise RequestError(404, 'Blog id not found')
        else:
            verify_account_by_id(blog['author_id'])
            blog = db.update_blog(blog_id, title, content)

            response = jsonify(blog)

        return response


class AccountsView(MethodView):
    """
    This view handles all the /api / accounts / requests.
    """

    def get(self, account_id):
        """
        Handle GET requests.
        Returns JSON representing all of the accounts if account_id is None,
        or a single account if account_id is not None.
        :param account_id: id of a account, or None for all accounts
        :return: JSON response
        """

        db = get_db()
        if db.get_all_accounts() == []:
            response = jsonify([])
        else:
            log_in()
            if account_id is None:
                response = jsonify(db.get_all_accounts())
            else:
                account = db.get_account_by_id(account_id)

                if account is not None:
                    response = jsonify(account)
                else:
                    raise RequestError(404, 'Account ID not found')

        return response

    def post(self):
        """
        Handles a POST request to insert a new account. Returns a JSON
        response representing the new account.
        The account username, password must be provided in the requests's
        form data.
        :return: a response containing the JSON representation of the account
        """

        db = get_db()
        if 'username' not in request.form:
            raise RequestError(422, 'username required')
        elif 'password' not in request.form:
            raise RequestError(422, 'password required')
        else:
            response = jsonify(db.insert_account(request.form['username'],
                                                 request.form['password']))

        return response

    def delete(self, account_id):
        """
        Handle DELETE requests. id must be provided

        :param account_id: id of a account
        :return: JSON response
        """

        db = get_db()
        verify_account_by_id(account_id)
        db.delete_account(account_id)
        response = jsonify("Delete Successfully")

        return response

    def patch(self, account_id):
        """
        Handles a PATCH request to update password for an account.
        Returns a JSON response representing the updated account.

        New password must be provided in the requests's form data.

        :param account_id: id of a blog
        :return: a response containing the JSON representation of the
        updated account
        """

        db = get_db()
        if 'password' not in request.form:
            raise RequestError(422, 'new password must be provided')

        account = db.get_account_by_id(account_id)

        if account is not None:
            verify_account_by_id(account_id)
            up_account = db.update_account(account_id, request.form['password'])
            response = jsonify(up_account)
        else:
            raise RequestError(404, 'Account id not found')

        return response


class CommentsView(MethodView):
    """
    This view handles all the /api / comments / requests.
    """

    def get(self, comment_id):
        """
        Handle GET requests.
        Returns JSON representing all of the comments if comment_id is None,
        or a single comment if comment_id is not None.
        :param comment_id: id of a comment, or None for all comments
        :return: JSON response
        """

        db = get_db()
        if db.get_all_accounts() == []:
            response = jsonify([])
        else:
            log_in()
            if comment_id is None:
                response = jsonify(db.get_all_rows('comment'))

                return response
            else:
                comment = db.query_by_id('comment', comment_id)
                
                if comment is not None:
                    response = jsonify(comment)
                else:
                    raise RequestError(404, 'Comment ID not found')

        return response

    def post(self):
        """
        Handles a POST request to insert a new comment. Returns a JSON
        response representing the new comment.
        The comment's content, blog_id, author_id must be provided in the
        requests's form data.
        :return: a response containing the JSON representation of the comment
        """

        db = get_db()
        if 'author_id' not in request.form:
            raise RequestError(422, 'author_id required')
        elif 'blog_id' not in request.form:
            raise RequestError(422, 'blog_id required')
        elif 'content' not in request.form:
            raise RequestError(422, 'content required')
        else:
            verify_account_by_id(request.form['author_id'])
            insert = db.insert_comment(request.form['blog_id'],
                                       request.form['author_id'],
                                       request.form['content'])
            if insert is None:
                raise RequestError(404, 'blog_id not found')
            else:
                response = jsonify(insert)

        return response

    def delete(self, comment_id):
        """
        Handle DELETE requests. id must be provided

        :param comment_id: id of a comment
        :return: JSON response
        """

        db = get_db()
        comment = db.query_by_id('comment', comment_id)

        if comment is not None:
            verify_account_by_id(comment['author_id'])
            db.delete_comment(comment_id)
            response = jsonify('Delete Successfully')
        else:
            raise RequestError(404, 'comment not found')

        return response

    def patch(self, comment_id):
        """
        Handles a PATCH request to update a comment. Returns a JSON
        response representing the updated comment.

        The new content must be provided in the requests's form data.

        :param comment_id: id of a comment
        :return: a response containing the JSON representation of the
        updated comment
        """

        db = get_db()
        if 'content' not in request.form:
            raise RequestError(422, 'Content must be provided')
        else:
            content = request.form['content']

        comment = db.query_by_id('comment', comment_id)

        if comment is not None:
            verify_account_by_id(comment['author_id'])
            comment = db.update_comment(comment_id, content)
            response = jsonify(comment)
        else:
            raise RequestError(404, 'Comment not found')

        return response


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """
    Serves a page for signing up.
    """
    """
    Serves a page for logging in when the request is GET.
    Creates a new account when the request is POST.
     """
    db = get_db()

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username is None or password is None:
            raise RequestError(422, 'Username and password must be provided')

        if db.get_account_by_username(username) is not None:
            raise RequestError(422, 'Username already exists')

        db.insert_account(username, password)

        return render_template('login.html')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def show_login_page():
    """
    Serves a page for logging in when the request is GET.
    Creates a new account when the request is POST.
    """
    db = get_db()
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username is None or password is None:
            raise RequestError(422, 'Username and password must be provided')

        browser_log_in(username, password)

        account = db.get_account_by_username(username)
        login_user(User(account['id']))

        blogs = db.get_all_rows('blog')
        blogs_with_authors = []

        for blog in blogs:
            blogs_with_authors.append(db.get_blog_by_id(blog['id']))

        blogs_with_authors.reverse()
        authors = db.get_all_accounts()

        return render_template('homepage.html', blogs=blogs_with_authors,
                               author=authors[0])


@app.route('/', methods=['GET', 'POST'])
@login_required
def show_home_page():
    """
    Serves the homepage containing all the blogs.
    When the request is POST, inserts a new blog into the database.
    """
    # global logged_in_username

    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if title is None:
            raise RequestError(422, 'Title must be provided')

        if content is None:
            raise RequestError(422, 'Content must be provided')

        author_id = current_user.id
        db.insert_blog(title, content, author_id)

    blogs = db.get_all_rows('blog')
    blogs_with_authors = []

    for blog in blogs:
        blogs_with_authors.append(db.get_blog_by_id(blog['id']))

    blogs_with_authors.reverse()
    authors = db.get_all_accounts()

    return render_template('homepage.html', blogs=blogs_with_authors,
                           author=authors[0])


@app.route('/blogs/<id>', methods=['GET', 'POST'])
@login_required
def show_blog(id):
    """
    Serves a page that shows a blog and its comments.
    When the request is POST, inserts a comment into the database.

    :param id: ID of the blog
    """
    db = get_db()

    blog = db.get_blog_by_id(id)

    if blog is None:
        raise RequestError(404, 'Blog ID not found')

    if request.method == 'POST':
        content = request.form['content']

        if content is None:
            raise RequestError(422, 'Content must be provided')

        author_id = current_user.id
        db.insert_comment(id, author_id, content)

    comments = db.get_comments_from_blog(id)
    comments_with_author = []

    for comment in comments:
        comments_with_author.append(db.get_comment_by_id(comment['id']))

    comments.reverse()
    authors = db.get_all_accounts()

    return render_template('post.html', blog=blog,
                           comments=comments_with_author, author=authors[0])


@app.route('/authors/<id>')
@login_required
def show_author(id):
    """
    Serves a page showing all the blogs of a specific author.

    :param id: ID of the author
    """
    db = get_db()

    account = db.query_by_id('account', id)

    if account is None:
        raise RequestError(404, 'Author ID not found')

    blogs = db.get_blog_by_author(id)
    author = db.query_by_id('account', id)
    authors = db.get_all_accounts()
    blogs.reverse()

    return render_template('authors.html', blogs=blogs, authors=authors,
                           author=author)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('logout.html')


def main():
    """
    Provides a command-line interface for posting comments and blogs.
    """

    if len(sys.argv) != 1:
        sys.exit('Usage: {}'.format(sys.argv[0]))

    try:
        with app.app_context():
            account_id = log_in()
    except RequestError as e:
        sys.exit(e)

    request_url = 'http://127.0.0.1:5000/api'

    print('''Commands:
             B: post a blog
             C <id>: post a comment on the blog with given ID
             Q: quit''')

    c = input()

    while c != 'Q':
        if c == 'B':
            title = input('Title: ')
            content = input('Content: ')
            try:
                response = requests.post(request_url + '/blogs/',
                                         data={'title': title, 'content': content,
                                               'author_id': account_id})

                if response.status_code != 200:
                    sys.exit('Error in posting blog')

                print('Posting Blog Successfully!')

            except RequestError as e:
                sys.exit(e)

        elif c[0] == 'C':
            try:
                blog_id = c[2:]
            except IndexError:
                sys.exit('Usage: C <id>')

            try:
                blog_id = int(blog_id)
            except ValueError:
                sys.exit('Usage: C <id>')

            content = input('Content: ')
            try:
                response = requests.post(request_url + '/comments/',
                                         data={'content': content,
                                               'author_id': account_id,
                                               'blog_id': blog_id})
                if response.status_code != 200:
                    sys.exit('Error in posting comment')

                print('Posting Comment Successfully!')

            except RequestError as e:
                sys.exit(e)

        else:
            sys.exit('''Usage: 
                        B: post a blog
                        C <id>: post a comment on the blog with given ID
                        Q: quit''')

        c = input()


# Register AccountView as the handler for all the api/accounts/requests.
accounts_view = AccountsView.as_view('accounts_view')
app.add_url_rule('/api/accounts/', defaults={'account_id': None},
                 view_func=accounts_view, methods=['GET'])
app.add_url_rule('/api/accounts/', view_func=accounts_view, methods=['POST'])
app.add_url_rule('/api/accounts/<int:account_id>', view_func=accounts_view,
                 methods=['GET', 'PATCH', 'DELETE'])

# Register BlogsView as the handler for all the /blogs/ requests.
blogs_view = BlogsView.as_view('blogs_view')
app.add_url_rule('/api/blogs/', defaults={'blog_id': None},
                 view_func=blogs_view, methods=['GET'])
app.add_url_rule('/api/blogs/', view_func=blogs_view, methods=['POST'])
app.add_url_rule('/api/blogs/<int:blog_id>', view_func=blogs_view,
                 methods=['GET', 'PATCH', 'DELETE'])

# Register CommentsView as the handler for all the /comments/ requests.
comments_view = CommentsView.as_view('comments_view')
app.add_url_rule('/api/comments/', defaults={'comment_id': None},
                 view_func=comments_view, methods=['GET'])
app.add_url_rule('/api/comments/', view_func=comments_view, methods=['POST'])
app.add_url_rule('/api/comments/<int:comment_id>', view_func=comments_view,
                 methods=['GET', 'PATCH', 'DELETE'])


if __name__ == '__main__':
    main()
