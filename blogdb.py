import hashlib
import sqlite3
import time


class BlogDB:
    """
    This class provides an interface for interacting with a database of
    blogs.
    """

    def __init__(self, filename):
        """
        Creates a connection to the database stored at filename
        :param filename: the address of the database
        """
        self.filename = filename
        self._conn = self.connect_db()

    def connect_db(self):
        """
        Connects sqlite object with database
        :return: an sqlite connection object associated with the application's
        database file
        """

        conn = sqlite3.connect(self.filename)
        conn.row_factory = sqlite3.Row

        return conn

    def init_db(self):
        """
        Initializes blog database
        :return: None
        """

        blog_sql = '''
        DROP TABLE IF EXISTS account;
        CREATE TABLE account(id INTEGER PRIMARY KEY, username TEXT UNIQUE,
                             password TEXT);
        DROP TABLE IF EXISTS blog;
        CREATE TABLE blog(id INTEGER PRIMARY KEY, title TEXT, 
                          content TEXT, author_id INTEGER, time TEXT,
                          FOREIGN KEY(author_id) REFERENCES account(id));
        DROP TABLE IF EXISTS comment;
        CREATE TABLE comment(id INTEGER PRIMARY KEY, blog_id INTEGER,
                             author_id INTEGER, content TEXT, time TEXT,
                             FOREIGN KEY(blog_id) REFERENCES blog(id),
                             FOREIGN KEY(author_id) REFERENCES account(id));
        '''

        self._conn.cursor().executescript(blog_sql)

    @staticmethod
    def get_current_time():
        """
        Gets current time
        :return: string containing current time details
        """

        current_time = time.ctime()

        return current_time

    def get_all_rows(self, table_name):
        """
        Returns all of the rows from a table as a list of dictionaries. This is
        suitable for passing to jsonify().
        :param table_name: name of the table
        :return: list of dictionaries representing the table's rows
        """

        cur = self._conn.cursor()

        query = 'SELECT * FROM {}'.format(table_name)

        results = []

        for row in cur.execute(query):
            results.append(dict(row))

        return results

    def get_all_accounts(self):
        """
           Returns all attribute accounts except password as a list of
           dictionaries.
           This is suitable for passing to jsonify().
           :return: list of dictionaries representing the account's rows
           """

        cur = self._conn.cursor()

        query = 'SELECT id, username FROM account'

        results = []

        for row in cur.execute(query):
            results.append(dict(row))

        return results

    def query_by_id(self, table_name, item_id):
        """
        Get a row from a table that has a primary key attribute named id.
        Returns None if there is no such row.
        :param table_name: name of the table to query
        :param item_id: id of the row
        :return: a dictionary representing the row
        """

        cur = self._conn.cursor()

        query = 'SELECT * FROM {} WHERE id = ?'.format(table_name)

        cur.execute(query, (item_id,))

        row = cur.fetchone()

        if row is not None:
            return dict(row)
        else:
            return None

    def get_account_by_id(self, account_id):
        """
        Get an account except its password that has a primary key attribute
        named id. Returns None if there is no such row.
        :param account_id: id of the account
        :return: a dictionary representing the account
        """

        cur = self._conn.cursor()

        query = 'SELECT id, username FROM account WHERE id = ?'

        cur.execute(query, (account_id,))

        row = cur.fetchone()

        if row is not None:
            return dict(row)
        else:
            return None

    def get_account_by_username(self, username):
        """
        Gets the dictionary representing an account using its username. Returns
        None if the username is not in the database.

        :param username: username of the account
        :return: dictionary containing the account
        """

        cur = self._conn.cursor()
        query = 'SELECT * FROM account WHERE username = ?'
        cur.execute(query, (username,))
        row = cur.fetchone()

        if row is None:
            return None
        else:
            return dict(row)

    def get_blog_by_author(self, id):
        """
        Returns a list of blog posts posted by account with given ID
        :return: list of blog posts posted from account with given ID
        """

        cur = self._conn.cursor()

        blog_posts = []

        query = 'SELECT * FROM blog WHERE author_id = (?)'

        for row in cur.execute(query, (id,)):
            blog_posts.append(row)

        return blog_posts

    def get_comments_from_blog(self, id):
        """
        Returns a list of comments posted for a blog post with given ID
        :return: comments and associated information for blog with ID blog_id
        """

        cur = self._conn.cursor()

        comments = []

        query = 'SELECT * FROM comment WHERE blog_id = (?)'

        for row in cur.execute(query, (id,)):
            comments.append(row)

        return comments

    def get_blog_by_id(self, id):
        """
        Returns the dictionary representing a blog using its ID. The keys of the
        dictionary are 'title', 'content', 'username', 'time', author_id',
        'id'. Returns None if no entry in the blog table has the ID.

        :param id: ID of the blog
        :return: dictionary containing the blog
        """

        cur = self._conn.cursor()
        query = '''SELECT title, content, username, time, author_id, blog.id as id 
                   FROM blog, account 
                   WHERE blog.id = ? AND account.id = blog.author_id'''
        cur.execute(query, (id,))
        blog = cur.fetchone()

        if blog is not None:
            return dict(blog)
        else:
            return None

    def get_comment_by_id(self, id):
        """
        Gets a comment by its ID. The dictionary keys are 'content', 'time',
        'author_id' and 'username'. Returns None if there is no entry in the
        comment table with that ID.

        :param id: ID of the comment
        :return: dictionary containing the comment
        """

        cur = self._conn.cursor()
        query = '''SELECT content, time, username, author_id FROM comment, account 
                   WHERE comment.id = ? AND account.id = comment.author_id'''
        cur.execute(query, (id,))
        comment = cur.fetchone()

        if comment is not None:
            return dict(comment)
        else:
            return None

    def insert_blog(self, title, content, author_id):
        """
        Create new blog post. Account login/verification required before posting.
        :param title: name of post
        :param content: writing of post
        :param author_id: account ID of writer of post
        :return: dictionary representing new blog information
        """

        cur = self._conn.cursor()
        account = self.query_by_id('account', author_id)

        if account is None:
            return None

        time_posted = self.get_current_time()

        insert_query = '''
        INSERT INTO blog(title, content, author_id, time) VALUES(?, ?, ?, ?)
        '''
        cur.execute(insert_query, (title, content, author_id, time_posted))
        self._conn.commit()

        blog_id = cur.lastrowid
        return self.query_by_id('blog', blog_id)

    def insert_comment(self, blog_id, author_id, content):
        """
        Create comment on existing blog post. Account login/verification required
        before posting.
        :param blog_id: ID of blog comment is posted on
        :param author_id: ID of account from which the comment is being posted
        :param content: writing in the comment
        :return: dictionary representing new comment information
        """

        cur = self._conn.cursor()
        account = self.query_by_id('account', author_id)

        # Return None if author does not exist
        if account is None:
            return None

        # Return None if author does not exist
        if self.query_by_id('blog', blog_id) is None:
            return None

        time_posted = self.get_current_time()

        insert_query = '''
        INSERT INTO comment(blog_id, author_id, content, time) VALUES(?, ?, ?, ?)
        '''
        cur.execute(insert_query, (blog_id, author_id, content, time_posted))
        id = cur.lastrowid
        self._conn.commit()

        return self.query_by_id('comment', id)

    def insert_account(self, username, password):
        """
        Creates new account with unique username and associated password.
        :param username: new username (must not already exist)
        :param password: password for account
        :return: dictionary return inserted account except for its password
        """

        cur = self._conn.cursor()

        salt = '7jk'
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

        insert_query = '''
        INSERT INTO account(username, password) VALUES(?, ?)
        '''

        cur.execute(insert_query, (username, hashed_password))
        self._conn.commit()

        account_id = cur.lastrowid

        return self.get_account_by_id(account_id)

    def update_account(self, account_id, password):
        """
        Creates new account with unique username and associated password.
        :param account_id: id of the account want to modify
        :param password: password for account
        :return: dictionary return updated account except for its password
        """

        cur = self._conn.cursor()

        salt = '7jk'
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

        update_query = '''
        UPDATE account SET password = ? WHERE id = ?
        '''

        cur.execute(update_query, (hashed_password, account_id))
        self._conn.commit()

        return self.get_account_by_id(account_id)

    def update_blog(self, blog_id, blog_title, blog_content):
        """
        This is used to update a current blog. The account that posted the blog
        must be the one to update it, so the username and password of the user
        updating the blog are verified before continuing.
        :param blog_id: id of the blog to be updated
        :param blog_title: new name of the blog
        :param blog_content: new content of the blog
        :return: a dictionary containing the updated blog information
        """

        cur = self._conn.cursor()

        if self.query_by_id('blog', blog_id) is None:
            return None

        new_time = self.get_current_time()

        update_query_1 = '''
        UPDATE blog SET title = ? WHERE id = ?
        '''
        update_query_2 = '''
        UPDATE blog SET content = ? WHERE id = ?
        '''
        update_query_3 = '''
        UPDATE blog SET time = ? WHERE id = ?
        '''

        if blog_title is not None:
            cur.execute(update_query_1, (blog_title, blog_id,))
        if blog_content is not None:
            cur.execute(update_query_2, (blog_content, blog_id,))
        if new_time is not None:
            cur.execute(update_query_3, (new_time, blog_id,))
        self._conn.commit()

        return self.query_by_id('blog', blog_id)

    def update_comment(self, comment_id, comment_content):
        """
        This is used to update a current comment. The account that posted the
        comment must be the one to update it, so the username and password of
        the user updating the comment are verified before continuing.
        :param comment_id: id of the comment to be updated
        :param comment_content: new content of the comment
        :return: a dictionary containing the updated comment information
        """

        cur = self._conn.cursor()
        if self.query_by_id('comment', comment_id) is None:
            return None

        new_time = self.get_current_time()

        update_query_1 = '''
        UPDATE comment SET content = ? WHERE id = ?
        '''
        update_query_2 = '''
        UPDATE comment SET time = ? WHERE id = ?
        '''

        if comment_content is not None:
            cur.execute(update_query_1, (comment_content, comment_id,))
        if new_time is not None:
            cur.execute(update_query_2, (new_time, comment_id,))
        self._conn.commit()

        return self.query_by_id('comment', comment_id)

    def delete_blog(self, blog_id):
        """
        Deletes all comments and blog with given blog_id, the account that
        this ID is related to (blog's/comment's author or account owner) must
        verify their username and password before continuing.
        :param blog_id: ID of blog
        """

        cur = self._conn.cursor()

        query1 = 'DELETE FROM comment WHERE blog_id = ?'
        query2 = 'DELETE FROM blog WHERE id = ?'
        cur.execute(query1, (blog_id,))
        cur.execute(query2, (blog_id,))
        self._conn.commit()

    def delete_account(self, account_id):
        """
        Deletes all comments and blogs and account with given author_id. The
        owner of the account that this ID is related to (blog's/comment's author
        or account owner) must verify their username and password before
        continuing.

        :param account_id: ID of account you want to delete
        """

        cur = self._conn.cursor()

        query1 = 'SELECT id FROM blog WHERE author_id = ?'
        query2 = 'DELETE FROM comment WHERE blog_id = ?'
        query3 = 'DELETE FROM comment WHERE author_id = ?'
        query4 = 'DELETE FROM blog WHERE author_id =?'
        query5 = 'DELETE FROM account WHERE id = ?'

        results = []
        for row in cur.execute(query1, (account_id,)):
            results.append(dict(row))

        for item in results:
            cur.execute(query2, (item['id'],))

        cur.execute(query3, (account_id,))

        cur.execute(query4, (account_id,))

        cur.execute(query5, (account_id,))

        self._conn.commit()

    def delete_comment(self, comment_id):
        """
        Deletes a comment in the database using its ID.

        :param comment_id: ID of the comment
        :return: None
        """

        cur = self._conn.cursor()

        query = 'DELETE FROM comment WHERE id = ?'

        cur.execute(query, (comment_id,))

        self._conn.commit()
