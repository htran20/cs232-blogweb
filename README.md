# Blog Project

This repository hosts a Flask app that serves a website for 
hosting blogs and provides an API for interacting with the 
database. Functionality includes:
* Create an account
* Post a blog
* Post a comment
* Edit / delete accounts, blogs, comments

Users have to run command `flask initdb` to initiate the database 
before using it.

## Browser Interface
To use the website, the user must start at the log in page: 
http://127.0.0.1:5000/login

After creating an account and/or logging in, users will be 
redirected to the homepage, which shows all the blogs ordered 
by time posted, from newest to oldest. From the homepage, users 
can post a new blog. On each blog, there is a URL leading to 
the main page of the blog, where users can comment on it.

Users can also view blogs by author by clicking on the authors 
tab and choose an author to view.

Users will remained logged in until the end of the session unless
 they go to the log in page or click on log out.
 
## API
Documentations for the API can be found in main.py. Any request 
to a protected function will prompt the user for their username 
and password. Requests made when the database is empty will not 
require account verification.


## Command-line interface
Users can run the application using the command `Python3 main.py`.
The application prompts the user for their username and password, 
then prints out the usage message.

* `B`: post a new blog
* `C <id>`: post a new comment for blog with given ID
* `Q`: quit


## To run tests:
`python3 -m pytest test_flask_app.py`


`python3 -m pytest test_database.py`
