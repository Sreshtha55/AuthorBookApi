from fastapi.testclient import TestClient
import urllib.parse
from main import app

client = TestClient(app)

def test_create_author():
    body1={
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "email": "test@gmail.com",
        "age": 20,
        "password": "testing123"
    }
    body2={
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "email": "test@gmail.com",
        "age": 20,
        "password": "stringst"
    }

    body3={
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "email": "test@gmail.com",
        "age": 20,
        "password": "tes"
    }

    body4={
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "password": "testing123"
    }

    body5={
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "email": "test1@gmail.com"
    }

    body6={
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "email": "test1",
        "password":"testing123"
    }

    body7={
        "email": "test@gmail.com",
        "password":"testing123"
    }


    return_json_keys=["_id","first_name","last_name","email","age"]

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    login_user1 = client.post("/author",headers=headers, json=body1)
    token_data1=login_user1.json()

    assert login_user1.status_code == 201 , "response code returned is not 201"
    assert set(return_json_keys)==set(token_data1.keys()) , "access_token key is not found in login api response"


    login_user2 = client.post("/author",headers=headers, json=body2)
    token_data2=login_user2.json()
    assert login_user2.status_code == 422 , "response code returned is not 200"
    assert token_data2 == {
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "password"
      ],
      "msg": "Value error, Password must contain both letters and digits",
      "input": "stringst",
      "ctx": {
        "error": {}
      },
      "url": "https://errors.pydantic.dev/2.1/v/value_error"
    }
  ]
}

    login_user3 = client.post("/author",headers=headers, json=body3)
    token_data3=login_user3.json()
    assert login_user3.status_code == 422 , "response code returned is not 200"
    assert token_data3 == {
  "detail": [
    {
      "type": "string_too_short",
      "loc": [
        "body",
        "password"
      ],
      "msg": "String should have at least 8 characters",
      "input": "tes",
      "ctx": {
        "min_length": 8
      },
      "url": "https://errors.pydantic.dev/2.1/v/string_too_short"
    }
  ]
}

    login_user4 = client.post("/author",headers=headers, json=body4)
    token_data4=login_user4.json()
    assert login_user4.status_code == 422 , "response code returned is not 200"
    assert token_data4 == {
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "email"
      ],
      "msg": "Field required",
      "input": {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "password": "testing123"
      },
      "url": "https://errors.pydantic.dev/2.1/v/missing"
    }
  ]
}

    login_user5 = client.post("/author",headers=headers, json=body5)
    token_data5=login_user5.json()
    assert login_user5.status_code == 422 , "response code returned is not 200"
    assert token_data5 == {
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "password"
      ],
      "msg": "Field required",
      "input": {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "email": "test1@gmail.com"
      },
      "url": "https://errors.pydantic.dev/2.1/v/missing"
    }
  ]
}

    login_user6 = client.post("/author",headers=headers, json=body6)
    token_data6=login_user6.json()
    assert login_user6.status_code == 422 , "response code returned is not 200"
    assert token_data6 == {
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "email"
      ],
      "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",
      "input": "test1",
      "ctx": {
        "reason": "The email address is not valid. It must have exactly one @-sign."
      }
    }
  ]
}

    login_user7 = client.post("/author",headers=headers, json=body7)
    token_data7=login_user7.json()
    assert login_user7.status_code == 400 , "response code returned is not 200"
    assert token_data7 == {
  "detail": "You are already registered, either register with a different email or please login with your registered email . If wants to change password then please use endpoint http://testserver/author/author/password_change"
}

