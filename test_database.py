"""
This module contains tests for the database in blogdb.py
Run with: python3 -m pytest test_database.py
"""

import pytest
import tempfile
import os

import blogdb


@pytest.fixture
def test_client():
    db_fd, tmp_fle = tempfile.mkstemp()
    test_client = blogdb.BlogDB(tmp_fle)

    yield test_client

    os.close(db_fd)
    os.unlink(tmp_fle)


def test_empty_database(test_client):
    """
    Tests the empty database
    :param test_client: database test client
    """
    test_client.init_db()
    response = test_client.get_all_rows('account')
    assert response == []
    response = test_client.get_all_rows('blog')
    assert response == []
    response = test_client.get_all_rows('comment')
    assert response == []


def test_insert(test_client):
    """
    Tests the insert function for account, blog, comment
    :param test_client: database test client
    """
    test_client.init_db()
    comment = {
        'blog_id': 1,
        'author_id': 1,
        'content': 'This blog is nice',
    }
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger 4',
        'content': 'Iron man still alive',
        'author_id': 1,
    }
    expected_comment = {
        'id': 1,
        'content': 'This blog is nice',
        'author_id': 1,
        'blog_id': 1,
    }
    expected_account = {
        'id': 1,
        'username': 'htran20',
    }
    expected_blog = {
        'id': 1,
        'title': 'Avenger 4',
        'content': 'Iron man still alive',
        'author_id': 1,
    }

    response = test_client.insert_account(*account.values())
    for key, value in expected_account.items():
        assert response[key] == value

    response = test_client.insert_blog(*blog.values())
    for key, value in expected_blog.items():
        assert response[key] == value

    response = test_client.insert_comment(*comment.values())
    for key, value in expected_comment.items():
        assert response[key] == value


def test_update(test_client):
    """
    Tests the update function for account, blog, comment
    :param test_client: database test client
    """
    test_client.init_db()
    comment = {
        'blog_id': 1,
        'author_id': 1,
        'content': 'This blog is nice',
    }
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger 4',
        'content': 'Iron man still alive',
        'author_id': 1,
    }
    update_comment = {
        'id': 1,
        'content': 'This blog is terrible',
    }
    update_blog = {
        'id': 1,
        'title': 'Spiderman',
        'content': 'Not Peter Parker anymore',
    }
    update_account = {
        'id': 1,
        'password': '123hai',
    }
    expected_comment = {
        'id': 1,
        'content': 'This blog is terrible',
        'author_id': 1,
        'blog_id': 1,
    }
    expected_account = {
        'id': 1,
        'username': 'htran20',
    }
    expected_blog = {
        'id': 1,
        'title': 'Spiderman',
        'content': 'Not Peter Parker anymore',
        'author_id': 1,
    }
    test_client.insert_account(*account.values())
    test_client.insert_blog(*blog.values())
    test_client.insert_comment(*comment.values())

    response = test_client.update_account(*update_account.values())
    for key, value in expected_account.items():
        assert response[key] == value

    response = test_client.update_blog(*update_blog.values())
    for key, value in expected_blog.items():
        assert response[key] == value

    response = test_client.update_comment(*update_comment.values())
    for key, value in expected_comment.items():
        assert response[key] == value


def test_delete(test_client):
    """
    Tests the delete function for account, blog, comment
    :param test_client: database test client
    """
    test_client.init_db()
    comment = {
        'blog_id': 1,
        'author_id': 1,
        'content': 'This blog is nice',
    }
    account = {
        'username': 'htran20',
        'password': 'haha1232',
    }
    blog = {
        'title': 'Avenger 4',
        'content': 'Iron man still alive',
        'author_id': 1,
    }
    test_client.insert_account(*account.values())
    test_client.insert_blog(*blog.values())
    test_client.insert_comment(*comment.values())

    test_client.delete_comment(1)
    response = test_client.get_all_rows('comment')
    assert response == []

    test_client.delete_blog(1)
    response = test_client.get_all_rows('blog')
    assert response == []

    test_client.delete_account(1)
    response = test_client.get_all_rows('account')
    assert response == []
