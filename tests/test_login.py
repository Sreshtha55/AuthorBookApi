from fastapi.testclient import TestClient
import urllib.parse
from main import app

client = TestClient(app)

def test_init_user():

    # User satisfies the condition and sends the correct username and password
    x={
        "username": "harsh@gmail.com",
        "password": "testing123"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    x=urllib.parse.urlencode(x)
    login_user = client.post("/login",headers=headers, data=x)
    token_data=login_user.json()
    print(token_data)
    assert login_user.status_code == 200 , "response code returned is not 200"
    assert "access_token" in login_user.json() , "access_token key is not found in login api response"

    # User sends with the incorrect username
    x={
        "username": "harsh123@gmail.com",
        "password": "testing123"
    }
    x=urllib.parse.urlencode(x)
    login_user = client.post("/login",headers=headers, data=x)
    token_data=login_user.json()
    print(token_data)
    assert login_user.status_code == 400 , "response code returned is not 200"
    assert "access_token" not in login_user.json() , "access_token key is not found in login api response"

    # User sends with the incorrect password
    x={
        "username": "harsh@gmail.com",
        "password": "testing12345"
    }
    x=urllib.parse.urlencode(x)
    login_user = client.post("/login",headers=headers, data=x)
    token_data=login_user.json()
    print(token_data)
    assert login_user.status_code == 400 , "response code returned is not 200"
    assert "access_token" not in login_user.json() , "access_token key is not found in login api response"