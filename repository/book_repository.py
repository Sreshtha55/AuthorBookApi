from models import bookmodel
from config.db import conn
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse
from schemas import *
from datetime import datetime
from bson import ObjectId


def create(request: bookmodel.Book,email:str):
    mybook = conn["BookDB"]
    record = request.model_dump(exclude_unset=True)
    if record["title"] not in mybook.books.distinct("title"):
        record.update({"writer":email,"published_date":datetime.today().replace(microsecond=0)})
        new_book = mybook.books.insert_one(record)
        changed_new_book = mybook.books.find_one({"_id": new_book.inserted_id},{"writer":0})

        mybook.authors.update({"email": record["writer"]}, {"$push": {"books": changed_new_book}})
        new_book = mybook.books.find_one({"_id": new_book.inserted_id})
        return DictSerializer(new_book)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please change the title because another book with this title is already taken!")


def show_all(email:str,search:str| None=None, limit:int | None=None):
    mybook = conn["BookDB"]
    if not search:
        get_book = mybook.authors.find_one({"email": email},{"books":1})
        if "books" not in get_book:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this Author email id '{email}'")
        return (ListSerializer(get_book["books"]))
    else:
        mybook.books.create_index([("title","text")])
        if not limit:
            result = mybook.books.find_one({"$and":[{"writer": email},{"$text":{"$search":search}}]})
        else:
            result = mybook.books.find_one({"$and": [{"writer": email}, {"$text": {"$search": search}}]}).limit(limit)
        if result == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No books found!")
        return (ListSerializer(result))

def show_by_title(title: str):
    mybook = conn["BookDB"]
    get_book = mybook.books.find_one({"title": title})
    if get_book== None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this title '{title}'")
    return DictSerializer(get_book)

def patch(id:str, request: bookmodel.UpdateBook, email:str):
    mybook = conn["BookDB"]
    if not mybook.books.find_one({"$and":[{"_id": ObjectId(id)},{"writer":email}]}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this Author with this book id '{id}'")
    body = request.model_dump(exclude_unset=True)
    if body=={}:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Nothing updated! Please update atleast one field")
    new_body = {
        key: value for key, value in body.items()
        if value is not None
    }
    authors = mybook.books.find_one_and_update({"_id": ObjectId(id)},{"$set":new_body})
    for key,value in new_body.items():
        update_book_field_in_authors=mybook.authors.update_one({"books._id":ObjectId(id)},{ "$set": {f"books.$.{key}":value}})
    return JSONResponse(content=f"Updated book data provided for book id {id}")

def delete(id: str, email:str):
    mybook = conn["BookDB"]
    delete_book= mybook.books.find_one_and_delete({"_id": ObjectId(id), "writer": email})
    if delete_book == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Incorrect ID provided. Please retry again with the correct id")
    delete_book_from_authors_collection = mybook.authors.update_one({"books._id":ObjectId(id)},{ "$pull": { "books": { "_id": ObjectId(id) } }})
