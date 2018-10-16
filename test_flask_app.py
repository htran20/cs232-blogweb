"""
This module contains tests for the Flask app in main.py
Run with: python3 -m pytest test_flask_app.py
"""
import pytest
import tempfile
import json
import os
import mock

import main


@pytest.fixture
def test_client():
    db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
    main.app.testing = True
    test_client = main.app.test_client()

    with main.app.app_context():
        db = main.get_db()
        db.init_db()

    yield test_client

    os.close(db_fd)
    os.unlink(main.app.config['DATABASE'])


def mock_input(prompt):
    """
    function that selects the next input depending on the prompt:
    :param prompt: the prompt ask for input
    :return: the compatible input to the prompt
    """
    if "username" in prompt.lower():
        return 'htran20'
    if "password" in prompt.lower():
        return 'haha1232'


def test_no_accounts(test_client):
    """
    Tests GET of none account.
    :param test_client: flask test client
    """
    response = test_client.get('/api/accounts/')

    # Make sure we got a status code of 200
    assert response.status_code == 200

    # The body of the response is JSON, so we turn it from a string into a JSON
    # object.
    response_json = json.loads(response.data)

    # Since no accounts were posted, this should be an empty list
    assert response_json == []


def test_one_account(test_client):
    """
    Tests POST of an account.
    :param test_client: flask test client
    """

    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }

    response = test_client.post('/api/accounts/', data=account)

    assert response.status_code == 200

    response_json = json.loads(response.data)

    # The response JSON should have these 4 keys
    expected_keys = ('id', 'username')
    for key in expected_keys:
        assert key in response_json

    # This should be the structure of the JSON, minus the timestamp. We won't
    # check the timestamp because we won't know what it is.
    expected_values = {
        'id': 1,
        'username': 'htran20',
    }

    for key, value in expected_values.items():
        assert response_json[key] == value


def test_update_account(test_client):
    """
    Tests PATCH of an account.
    :param test_client: flask test client
    """
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    update_account = {
        'password': '123hai',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):

        response = test_client.patch('/api/accounts/1', data=update_account)
        assert response.status_code == 200

        response_json = json.loads(response.data)

        # The response JSON should have these 4 keys
        expected_keys = ('id', 'username',)
        for key in expected_keys:
            assert key in response_json

        expected_values = {
            'id': 1,
            'username': 'htran20',
        }

        for key, value in expected_values.items():
            assert response_json[key] == value


def test_no_blogs(test_client):
    """
    Tests GET of none blog.
    :param test_client: flask test client
    """
    response = test_client.get('/api/blogs/')

    with mock.patch.object(main, 'input', mock_input):
        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert response_json == []


def test_one_blog(test_client):
    """
    Tests POST of a blog.
    :param test_client: flask test client
    """

    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger: Infiniy war',
        'author_id': 1,
        'content': 'Thanos destroys half the universe wiht one finger flick!',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):

        response = test_client.post('/api/blogs/', data=blog)

        assert response.status_code == 200

        response_json = json.loads(response.data)

        # The response JSON should have these 4 keys
        expected_keys = ('id', 'title', 'author_id', 'content', 'time')
        for key in expected_keys:
            assert key in response_json

        expected_values = {
            'id': 1,
            'title': 'Avenger: Infiniy war',
            'content': 'Thanos destroys half the universe wiht one finger flick!',
            'author_id': 1,
        }

        for key, value in expected_values.items():
            assert response_json[key] == value


def test_update_one_blog(test_client):
    """
    Tests PATCH of a blog.
    :param test_client: flask test client
    """
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger: Infiniy war',
        'author_id': 1,
        'content': 'Thanos destroys half the universe wiht one finger flick!',
    }
    update_blog = {
        'content': 'Iron man still alive',
        'title': 'Avenger 4',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):

        test_client.post('/api/blogs/', data=blog)

        response = test_client.patch('/api/blogs/1', data=update_blog)
        assert response.status_code == 200

        response_json = json.loads(response.data)

        # The response JSON should have these 4 keys
        expected_keys = ('id', 'title', 'author_id', 'content', 'time')
        for key in expected_keys:
            assert key in response_json

        expected_values = {
            'id': 1,
            'title': 'Avenger 4',
            'content': 'Iron man still alive',
            'author_id': 1,
        }

        for key, value in expected_values.items():
            assert response_json[key] == value


def test_no_comments(test_client):
    """
    Tests GET of none comment.
    :param test_client: flask test client
    """
    # Here is how to use the test client to simulate a GET request
    response = test_client.get('/api/comments/')

    with mock.patch.object(main, 'input', mock_input):
        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert response_json == []


def test_one_comment(test_client):
    """
    Tests POST of a comment.
    :param test_client: flask test client
    """

    comment = {
        'content': 'This blog is nice',
        'author_id': 1,
        'blog_id': 1,
    }
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger: Infiniy war',
        'author_id': 1,
        'content': 'Thanos destroys half the universe wiht one finger flick!',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):

        test_client.post('/api/blogs/', data=blog)

        response = test_client.post('/api/comments/', data=comment)
        assert response.status_code == 200

        response_json = json.loads(response.data)

        # The response JSON should have these 4 keys
        expected_keys = ('id', 'blog_id', 'author_id', 'content', 'time')
        for key in expected_keys:
            assert key in response_json

        expected_values = {
            'id': 1,
            'content': 'This blog is nice',
            'author_id': 1,
            'blog_id': 1,
        }

        for key, value in expected_values.items():
            assert response_json[key] == value


def test_update_one_comment(test_client):
    """
    Tests PATCH of a comment.
    :param test_client: flask test client
    """

    update_comment = {
        'content': 'This blog is terrible',
    }
    comment = {
        'content': 'This blog is nice',
        'author_id': 1,
        'blog_id': 1,
    }
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger: Infiniy war',
        'author_id': 1,
        'content': 'Thanos destroys half the universe wiht one finger flick!',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):

        test_client.post('/api/blogs/', data=blog)
        test_client.post('/api/comments/', data=comment)

        response = test_client.patch('/api/comments/1', data=update_comment)
        assert response.status_code == 200

        response_json = json.loads(response.data)

        # The response JSON should have these 4 keys
        expected_keys = ('id', 'blog_id', 'author_id', 'content', 'time')
        for key in expected_keys:
            assert key in response_json

        expected_values = {
            'id': 1,
            'content': 'This blog is terrible',
            'author_id': 1,
            'blog_id': 1,
        }

        for key, value in expected_values.items():
            assert response_json[key] == value


def test_delete_comments(test_client):
    """
    Tests DELETE of a comment.
    :param test_client: flask test client
    """
    comment = {
        'content': 'That blog is nice',
        'author_id': 1,
        'blog_id': 1,
    }
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger: Infiniy war',
        'author_id': 1,
        'content': 'Thanos destroys half the universe wiht one finger flick!',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):
        test_client.post('/api/blogs/', data=blog)
        test_client.post('/api/comments/', data=comment)
        response = test_client.delete('/api/comments/1')

        # Make sure we got a status code of 200
        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert response_json == 'Delete Successfully'


def test_delete_blogs(test_client):
    """
    Tests DELETE of a blog.
    :param test_client: flask test client
    """
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger: Infiniy war',
        'author_id': 1,
        'content': 'Thanos destroys half the universe wiht one finger flick!',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):
        test_client.post('/api/blogs/', data=blog)
        response = test_client.delete('/api/blogs/1')

        # Make sure we got a status code of 200
        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert response_json == 'Delete Successfully'


def test_delete_accounts(test_client):
    """
    Tests DELETE of an account.
    :param test_client: flask test client
    """
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }

    test_client.post('/api/accounts/', data=account)

    with mock.patch.object(main, 'input', mock_input):
        response = test_client.delete('/api/accounts/1')

        # Make sure we got a status code of 200
        assert response.status_code == 200

        response_json = json.loads(response.data)

        assert response_json == 'Delete Successfully'
