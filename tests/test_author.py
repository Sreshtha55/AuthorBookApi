from fastapi.testclient import TestClient
import urllib.parse
from main import app
from .confest import init_author_login
import pytest

client = TestClient(app)


@pytest.mark.create_author
def test_create_author():
    # Below body satisfies all the required
    body1 = {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "email": "test@gmail.com",
        "age": 20,
        "password": "testing123"
    }

    # Below Body Password field must contain both letters and digits
    body2 = {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "email": "test@gmail.com",
        "age": 20,
        "password": "stringst"
    }

    # Below body password field has does not have 8 characters
    body3 = {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "email": "test@gmail.com",
        "age": 20,
        "password": "tes"
    }

    # Below field does not have the required email field
    body4 = {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "password": "testing123"
    }

    # Below body does not have the required password field
    body5 = {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "email": "test1@gmail.com"
    }


    # Below body does not have the email field in email format
    body6 = {
        "first_name": "Sreshtha",
        "last_name": "Bhatt",
        "age": 20,
        "email": "test1",
        "password": "testing123"
    }

    # In the below body email is already registered
    body7 = {
        "email": "test@gmail.com",
        "password": "testing123"
    }

    return_json_keys = ["_id", "first_name", "last_name", "email", "age"]

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    create_user1 = client.post("/author", headers=headers, json=body1)
    data1 = create_user1.json()

    assert create_user1.status_code == 201, "response code returned is not 201"
    assert set(return_json_keys) == set(
        data1.keys()), "access_token key is not found in login api response"

    create_user2 = client.post("/author", headers=headers, json=body2)
    data2 = create_user2.json()
    assert create_user2.status_code == 422, "response code returned is not 422"
    assert data2 == {
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

    create_user3 = client.post("/author", headers=headers, json=body3)
    data3 = create_user3.json()
    assert create_user3.status_code == 422, "response code returned is not 422"
    assert data3 == {
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

    create_user4 = client.post("/author", headers=headers, json=body4)
    data4 = create_user4.json()
    assert create_user4.status_code == 422, "response code returned is not 422"
    assert data4 == {
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

    create_user5 = client.post("/author", headers=headers, json=body5)
    data5 = create_user5.json()
    assert create_user5.status_code == 422, "response code returned is not 422"
    assert data5 == {
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

    create_user6 = client.post("/author", headers=headers, json=body6)
    data6 = create_user6.json()
    assert create_user6.status_code == 422, "response code returned is not 422"
    assert data6 == {
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

    create_user7 = client.post("/author", headers=headers, json=body7)
    data7 = create_user7.json()
    assert create_user7.status_code == 400, "response code returned is not 400"
    assert data7 == {
        "detail": "You are already registered, either register with a different email or please login with your registered email . If wants to change password then please use endpoint http://testserver/author/author/password_change"
    }


@pytest.mark.change_password
def test_change_password(init_author_login):

    # In the below body the current password does not satisfies the 8 characters long validation
    body1 = {
        "current_password": "test",
        "new_password": "stringst123"
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    change_pass1 = client.put(
        "/author/password_change", headers=headers, json=body1)
    data1 = change_pass1.json()
    assert change_pass1.status_code == 422, "response code returned is not 422"
    assert data1 == {
        "detail": [
            {
                "type": "string_too_short",
                "loc": [
                    "body",
                    "current_password"
                ],
                "msg": "String should have at least 8 characters",
                "input": "test",
                "ctx": {
                    "min_length": 8
                },
                "url": "https://errors.pydantic.dev/2.1/v/string_too_short"
            }
        ]
    }

    ''' In the below body the current password satisfies the 8 characters 
    long validation but fails the requirement to conatin both letter and digits'''

    body2 = {
        "current_password": "testasmcnm",
        "new_password": "stringst123"
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    change_pass2 = client.put(
        "/author/password_change", headers=headers, json=body2)
    data2 = change_pass2.json()
    assert change_pass2.status_code == 422, "response code returned is not 422"
    assert data2 == {
        "detail": [
            {
                "type": "value_error",
                "loc": [
                    "body",
                    "current_password"
                ],
                "msg": "Value error, Password must contain both letters and digits",
                "input": "testasmcnm",
                "ctx": {
                    "error": {}
                },
                "url": "https://errors.pydantic.dev/2.1/v/value_error"
            }
        ]
    }

    # In the below body the new password does not satisfies the 8 characters long validation
    body3 = {
        "current_password": "testingsca123",
        "new_password": "test"
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    change_pass3 = client.put(
        "/author/password_change", headers=headers, json=body3)
    data3 = change_pass3.json()
    assert change_pass3.status_code == 422, "response code returned is not 422"
    assert data3 == {
        "detail": [
            {
                "type": "string_too_short",
                "loc": [
                    "body",
                    "new_password"
                ],
                "msg": "String should have at least 8 characters",
                "input": "test",
                "ctx": {
                    "min_length": 8
                },
                "url": "https://errors.pydantic.dev/2.1/v/string_too_short"
            }
        ]
    }

    ''' In the below body the new password satisfies the 8 characters 
    long validation but fails the requirement to conatin both letter and digits'''

    body4 = {
        "current_password": "testing1234",
        "new_password": "testxmnnck"
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    change_pass4 = client.put(
        "/author/password_change", headers=headers, json=body4)
    data4 = change_pass4.json()
    assert change_pass4.status_code == 422, "response code returned is not 422"
    assert data4 == {
        "detail": [
            {
                "type": "value_error",
                "loc": [
                    "body",
                    "new_password"
                ],
                "msg": "Value error, Password must contain both letters and digits",
                "input": "testxmnnck",
                "ctx": {
                    "error": {}
                },
                "url": "https://errors.pydantic.dev/2.1/v/value_error"
            }
        ]
    }

    # In the below body the current password does not mactches with the current password in DB
    body5 = {
        "current_password": "testingsca123",
        "new_password": "stringst123"
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    change_pass5 = client.put(
        "/author/password_change", headers=headers, json=body5)
    data5 = change_pass5.json()
    assert change_pass5.status_code == 400, "response code returned is not 400"
    assert data5 == {
        "detail": "Wrong current password provided! "
    }

    # The below body satisfies all the validation
    body6 = {
        "current_password": "testing123",
        "new_password": "testing1234"
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    change_pass6 = client.put(
        "/author/password_change", headers=headers, json=body6)
    data6 = change_pass6.json()
    assert change_pass6.status_code == 200, "response code returned is not 200"
    assert data6 == {
        "detail": "Your password has been updated successfully"
    }


@pytest.mark.get_author_profile
def test_get_author_profile(init_author_login):

    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    author_profile = client.get("/author/me", headers=headers)
    data = author_profile.json()
    assert author_profile.status_code == 200, "response code returned is not 200"
    assert data == {
        "first_name": "Harsh",
        "last_name": "Prasad",
        "email": "harsh@gmail.com",
        "age": 28
    }

    # In the below senario the user has not send its authorization header
    author_profile2 = client.get("/author/me")
    data2 = author_profile2.json()
    assert author_profile2.status_code == 401, "response code returned is not 401"
    assert data2 == {
        "detail": "Not authenticated"
    }


@pytest.mark.search_author_using_email
def test_search_author_using_email(init_author_login):

    # In the below senario the user has not send its authorization header
    header = {'Content-Type': 'application/json; charset=UTF-8'}
    search_profile = client.get("/author/profile/ok@gmail.com")
    data = search_profile.json()
    assert search_profile.status_code == 401, "response code returned is not 401"
    assert data == {
        "detail": "Not authenticated"
    }

    # In the below senario the user satisfies all the requirement
    header2 = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    search_profile2 = client.get(
        "/author/profile/ok@gmail.com", headers=header2)
    data2 = search_profile2.json()
    assert search_profile2.status_code == 200, "response code returned is not 200"
    assert data2 == {
        "first_name": "Testing",
        "last_name": "testing",
        "email": "ok@gmail.com",
        "age": 25,
        "books": [
            {
                "title": "Cindrella",
                "summary": "Story About Cindrella",
                "genres": [
                    "Story"
                ],
                "pages": 200
            }
        ]
    }

    # In the below senario the user has sent the email which is not registered.
    header3 = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    search_profile3 = client.get(
        "/author/profile/okdsd@gmail.com", headers=header3)
    data3 = search_profile3.json()
    assert search_profile3.status_code == 400, "response code returned is not 400"
    assert data3 == {
        "detail": "No Author found with email okdsd@gmail.com given."
    }


@pytest.mark.update_author
def test_update_author(init_author_login):

    # In the below scenario user is trying to send update request with empty body 
    body = {}
    header = {'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': f'Bearer {init_author_login}'}
    update_profile = client.patch("/author/me", headers=header, json=body)
    data = update_profile.json()
    assert update_profile.status_code == 400, "response code returned is not 400"
    assert data == {
        "detail": "Nothing updated! Please update atleast one field"
    }

    ''' In the below scenario user is trying to send update request in the body
      with only email field but email is already registered and taken by another user '''
    
    body2 = {
        "email": "ok@gmail.com"
    }
    header2 = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    update_profile2 = client.patch("/author/me", headers=header2, json=body2)
    data2 = update_profile2.json()
    assert update_profile2.status_code == 400, "response code returned is not 400"
    assert data2 == {
        "detail": "Email is already taken. Please retry with another email!"
    }

    # In the below scenario user satisfies all the requirement and he wants to update its first_name field only
    body3 = {
        "first_name": "Harsh"
    }
    header3 = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': f'Bearer {init_author_login}'}
    update_profile3 = client.patch("/author/me", headers=header3, json=body3)
    data3 = update_profile3.json()
    assert update_profile3.status_code == 200, "response code returned is not 200"
    assert data3 == {
        "first_name": "Harsh",
        "last_name": "Prasad",
        "email": "harsh@gmail.com",
        "age": 28
    }