from fastapi.testclient import TestClient
import urllib.parse
from main import app
from .confest import init_author_login
import pytest

client = TestClient(app)


@pytest.mark.create_book
def test_create_book(init_author_login):

    # In the below scenario user sends with emapty body , but title field is the required field
    body = {

    }
    header = {'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': f'Bearer {init_author_login}'}
    create_book = client.post("/book", headers=header, json=body)
    data = create_book.json()
    assert create_book.status_code == 422, "response code returned is not 422"
    assert data == {
        "detail": [
            {
                "type": "missing",
                "loc": [
                    "body",
                    "title"
                ],
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2.1/v/missing"
            }
        ]
    }

    # In the below senario the user has not send its authorization header
    header2 = {'Content-Type': 'application/json; charset=UTF-8'}
    create_book3 = client.post("/book", headers=header2, json=body)
    data3 = create_book3.json()
    assert create_book3.status_code == 401, "response code returned is not 401"
    assert data3 == {
        "detail": "Not authenticated"
    }

    # In the below scenario user satisfies all the requirement and sends his user id in the author_ids field
    body2 = {
        "title": "The secret",
        "summary": "Law of Attraction",
        "genres": [
            "Motivational"
        ],
        "pages": 200
    }

    create_book4 = client.post("/book", headers=header, json=body2)
    data4 = create_book4.json()
    del data4['published_date']
    del data4['_id']
    assert create_book4.status_code == 201, "response code returned is not 201"
    assert data4 == {
        "title": "The secret",
        "summary": "Law of Attraction",
        "genres": [
            "Motivational"
        ],
        "pages": 200,
        "author_ids": [
            "64df65bcce1f84b67732dd1c"
        ]
    }

    ''' In the below scenario user satisfies all the requirement and sends 
    the other user's user id in the author_ids field but not his own user id.'''

    body3 = {
        "title": "Rich Dad Poor Dad",
        "summary": "Secret of earning koney",
        "genres": [
            "Motivational"
        ],
        "pages": 300,
        "author_ids": [
            "64df510305e6867d94f9ca0b"
        ]
    }

    create_book5 = client.post("/book", headers=header, json=body3)
    data5 = create_book5.json()
    del data5['published_date']
    del data5['_id']
    assert create_book5.status_code == 201, "response code returned is not 201"
    assert data5 == {
        "title": "Rich Dad Poor Dad",
        "summary": "Secret of earning koney",
        "genres": [
            "Motivational"
        ],
        "pages": 300,
        "author_ids": [
            "64df510305e6867d94f9ca0b",
            "64df65bcce1f84b67732dd1c"
        ]
    }

    ''' In the below scenario user satisfies all the requirement and sends 
    the other user's user id in the author_ids field as well his own user id.'''
    body4 = {
        "title": "Test Title",
        "summary": "Test Summary",
        "genres": [
            "Test"
        ],
        "pages": 200,
        "author_ids": [
            "64df510305e6867d94f9ca0b",
            "64df65bcce1f84b67732dd1c"
        ]
    }

    create_book6 = client.post("/book", headers=header, json=body4)
    data6 = create_book6.json()
    del data6['published_date']
    del data6['_id']
    assert create_book6.status_code == 201, "response code returned is not 201"
    assert data6 == {
        "title": "Test Title",
        "summary": "Test Summary",
        "genres": [
            "Test"
        ],
        "pages": 200,
        "author_ids": [
            "64df510305e6867d94f9ca0b",
            "64df65bcce1f84b67732dd1c"
        ]
    }



# If there is few books under the author
@pytest.mark.showallbook
def test_showallbook(init_author_login):

    # If there is no books under the author
    header = {'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': f'Bearer {init_author_login}'}
    showallbooks = client.get("/book", headers=header)
    data = showallbooks.json()
    if showallbooks.status_code == 400:
        assert data == {
            "detail": "No Books found!"
        }
    else:
        assert showallbooks.status_code == 200, "response code returned is not 200"

    # Suppose the title under this author's books contains word "rich" in either lower or uppercase.
    showallbooks = client.get("/book", headers=header,
                              params={"search": "rich"})
    assert showallbooks.status_code == 200, "response code returned is not 200"

    # Suppose two or more than two books contains word "rich" in either lower or uppercase. But we want to limit our response to any int number.
    showallbooks = client.get("/book", headers=header,
                              params={"search": "rich", "limit": 1})
    assert showallbooks.status_code == 200, "response code returned is not 200"

    # Suppose we want all books to be shown, but we want to limit our response to any int number.
    showallbooks = client.get("/book", headers=header, params={"limit": 1})
    assert showallbooks.status_code == 200, "response code returned is not 200"


@pytest.mark.showallbookbytitle
def test_showallbookbytitle(init_author_login):

    header = {'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': f'Bearer {init_author_login}'}

    # If these title is under the logedin author
    title1 = {
        "Rich Dad Poor Dad",
        "Rich Country"
    }
    for i in title1:
        showallbooks = client.get(f"/book/{i}", headers=header)
        data=showallbooks.json()
        if showallbooks.status_code == 400:
            assert showallbooks.status_code == 400, "response code returned is not 400"
            assert data == {
                "detail": f"No Books found under this title '{i}'"
            }
        else:
            assert showallbooks.status_code == 200, "response code returned is not 200"

    # If there is no books under these title for the logedin author
    title2 = {
        "Sachin Tendulkar",
        "MS Dhoni"
    }
    for i in title2:
        showallbooks = client.get(f"/book/{i}", headers=header)
        data = showallbooks.json()
        assert showallbooks.status_code == 400, "response code returned is not 400"
        assert data == {
            "detail": f"No Books found under this title '{i}'"
        }


@pytest.mark.updatebook
def test_updatebook(init_author_login):
    header = {'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': f'Bearer {init_author_login}'}

    # These books Ids are under the logedin authors
    ids = [
        "64e4b6c0dfab117b6a338be9",
        "64e4b6d9dfab117b6a338bec"
    ]
    # But user sends update request with empty body
    body1 = {}
    for i in ids:
        updatebook = client.patch(f"/book/{i}", headers=header, json=body1)
        data = updatebook.json()
        assert updatebook.status_code == 400, "response code returned is not 400"
        assert data == {
            "detail": "Nothing updated! Please update atleast one field"
        }
    
    # User sends update request with all conditions satsfies
    body2 = {
        "title": "Test Title",
    }
    updatebook = client.patch(f"/book/{ids[0]}", headers=header, json=body2)
    data = updatebook.json()
    assert updatebook.status_code == 200, "response code returned is not 200"
    

    # User sends update request with title field to update but trying to update it with the already taken title
    updatebook = client.patch(f"/book/{ids[1]}", headers=header, json=body2)
    data = updatebook.json()
    assert updatebook.status_code == 400, "response code returned is not 400"
    assert data == {
        "detail": "The title is already taken!. Please change the title and then retry!"
    }

    # This book id is not under the logedin author and the user trying to send the update request with this id
    ids="64e336a638f88ae72099b073"
    updatebook = client.patch(f"/book/{ids}", headers=header, json=body2)
    data = updatebook.json()
    assert updatebook.status_code == 400, "response code returned is not 400"
    assert data == {
        "detail": f"No Books found under this Author with this book id '{ids}'"
    }

@pytest.mark.deletebook
def test_deletebook(init_author_login):   
    header = {'Content-Type': 'application/json; charset=UTF-8',
              'Authorization': f'Bearer {init_author_login}'}
    
    # This id is present in the db under this author. So this will succeed
    id="64e4b6c0dfab117b6a338be9"
    updatebook = client.delete(f"/book/{id}", headers=header)
    assert updatebook.status_code == 204 , "response code returned is not 204"

    # These id is either not under this author or not present anywhere in db
    ids=["64e336a638f88ae72099b073","64e5b9a9ff9ab5474b85a209"]
    for i in ids:
        updatebook = client.delete(f"/book/{i}", headers=header)
        data=updatebook.json()
        assert updatebook.status_code == 400 , "response code returned is not 400"
        assert data == {
            "detail": "Incorrect ID provided. Please retry again with the correct id"
        }



