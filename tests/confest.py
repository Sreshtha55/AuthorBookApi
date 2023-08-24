from fastapi.testclient import TestClient
import urllib.parse
from main import app
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def init_author_login():
    x={
        "username": "harsh@gmail.com",
        "password": "testing123"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    x=urllib.parse.urlencode(x)
    login_user = client.post("/login",headers=headers, data=x)
    print(login_user.json())
    token_data=login_user.json()["access_token"]
    return token_data