import pytest
from models import Blog, User


@pytest.fixture(scope='function')
def new_user():
    user = User("telosmachina", "1234secret")
    return user

