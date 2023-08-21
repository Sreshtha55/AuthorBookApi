from models import bookmodel
# from config.db import settings
from config.db import validate_db
from fastapi.exceptions import HTTPException
from fastapi import status,Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime
from bson import ObjectId
from bson import json_util
import json

def create(request: bookmodel.Book,current_user_dict,conn):
    mybook=conn["BookDB"]
    record = request.model_dump(exclude_unset=True)
    if "author_ids" not in record:
        record.update({"author_ids":current_user_dict["id"]})
    author_invalid_ids=[]
    for i in record["author_ids"]:
        # print(i)
        find_invalid_ids = mybook.authors.find_one({"_id":ObjectId(i)})
        # print(find_invalid_ids)
        if find_invalid_ids == None:
            author_invalid_ids.append(i)
    if author_invalid_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{author_invalid_ids} are not Valid ids.")
    if current_user_dict["id"] not in record["author_ids"]:
        record["author_ids"].append(current_user_dict["id"])
    if record["title"] not in mybook.books.distinct("title"):
        record.update({"published_date":datetime.today().replace(microsecond=0)})
        new_book = mybook.books.insert_one(record)
        changed_new_book = mybook.books.find_one({"_id": new_book.inserted_id})
        for i in record["author_ids"]:
            mybook.authors.update_one({"_id": ObjectId(i)}, {"$push": {"books": changed_new_book}})
        new_book = mybook.books.find_one({"_id": new_book.inserted_id})
        return json.loads(json_util.dumps(new_book))
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please change the title because another book with this title is already taken!")

def show_all(conn,id:str,search:str| None=None, limit:int | None=None):
    mybook=conn["BookDB"]
    if not search:
        if not limit:
            get_book = mybook.books.find({"author_ids":id})
        else:
            get_book=mybook.books.find({"author_ids": id}).limit(limit)
        if get_book.count()==0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No Books found!")
        return json.loads(json_util.dumps(get_book))
    else:
        mybook.books.create_index([("title","text")])
        if not limit:
            result = mybook.books.find({"$and":[{"author_ids": id},{"$text":{"$search":search}}]})
        else:
            result = mybook.books.find({"$and": [{"author_ids": id}, {"$text": {"$search": search}}]}).limit(limit)
        if result == None or result.count()==0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No books found!")
        return json.loads(json_util.dumps(result))

def show_by_title(title: str,conn):
    mybook=conn["BookDB"]
    get_book = mybook.books.find_one({"title": title})
    if get_book== None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this title '{title}'")
    return json.loads(json_util.dumps(get_book))

def patch(id:str, request: bookmodel.UpdateBook, current_user_id:str,conn):
    mybook=conn["BookDB"]
    if mybook.books.find({"$and":[{"_id": ObjectId(id)},{"author_ids":current_user_id}]}).count()==0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this Author with this book id '{id}'")
    body = request.model_dump(exclude_unset=True)
    if body=={}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Nothing updated! Please update atleast one field")
    updated_book_detail = mybook.books.update({"_id": ObjectId(id)},{"$set":body})
    updated_book_detail=mybook.books.find_one({"_id":ObjectId(id)})
    for key,value in body.items():
        update_book_field_in_authors=mybook.authors.update_many({"books._id":ObjectId(id)},{ "$set": {f"books.$.{key}":value}})
    return json.loads(json_util.dumps(updated_book_detail))

def delete(id: str, current_user_id:str,conn):
    mybook=conn["BookDB"]
    delete_book= mybook.books.find_one_and_delete({"_id": ObjectId(id), "author_ids": current_user_id})
    if delete_book == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Incorrect ID provided. Please retry again with the correct id")
    if len(delete_book["author_ids"]) == 1:
        delete_book_from_authors_collection = mybook.authors.update_many({"books._id":ObjectId(id)},{ "$pull": { "books": { "_id": ObjectId(id) } }})
    else:
        delete_book_from_authors_collection = mybook.authors.update_many({"books._id":ObjectId(id)},{ "$pull": { "books":{"author_ids" : current_user_id}}})

