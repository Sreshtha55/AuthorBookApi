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
import logging
from datetime import  datetime

now=datetime.now()
file_format = now.strftime("%Y-%m-%d-%H")

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler=logging.FileHandler(f"logs/bookapi_{file_format}.log")
formatter=logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def create(request: bookmodel.Book,current_user_dict,conn):
    logger.info(f"Create Book Request received!")
    mybook=conn["BookDB"]
    record = request.model_dump(exclude_unset=True)
    logger.info(f"Request body received is {record}")
    if "author_ids" not in record:
        logger.info(f"No author_ids provided")
        record.update({"author_ids":[current_user_dict["id"]]})
    logger.info(f"Validating the author ids provided")
    author_invalid_ids=[]
    for i in record["author_ids"]:
        # print(i)
        find_invalid_ids = mybook.authors.find_one({"_id":ObjectId(i)})
        # print(find_invalid_ids)
        if find_invalid_ids == None:
            author_invalid_ids.append(i)
    if author_invalid_ids:
        logger.error(f"The author_ids {author_invalid_ids} is not valid")
        logger.info(f"Create Book Request Finished")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{author_invalid_ids} are not Valid ids.")
    if current_user_dict["id"] not in record["author_ids"]:
        record["author_ids"].append(current_user_dict["id"])
    logger.info(f"Checking if the title given is unique")
    if record["title"] not in mybook.books.distinct("title"):
        logger.info(f"Title is unique")
        record.update({"published_date":datetime.today().replace(microsecond=0)})
        new_book = mybook.books.insert_one(record)
        logger.info(f"Record inserted in books collection")
        changed_new_book = mybook.books.find_one({"_id": new_book.inserted_id})
        for i in record["author_ids"]:
            mybook.authors.update_one({"_id": ObjectId(i)}, {"$push": {"books": changed_new_book}})
            logger.info(f"Record inserted in authors collection")
        new_book = mybook.books.find_one({"_id": new_book.inserted_id})
        logger.info(f"Create Book Request Finished")
        return json.loads(json_util.dumps(new_book))
    else:
        logger.error(f"Title is not unique, hence rejecting this request")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Please change the title because another book with this title is already taken!")

def show_all(conn,id:str,search:str| None=None, limit:int | None=None):
    logger.info(f"Get All Book Request received!")
    mybook=conn["BookDB"]
    if not search:
        logger.info(f"Search query argument is not given")
        if not limit:
            logger.info(f"Limit query argument is not given")
            logger.info(f"Checking if any book found under the loggedin author")
            get_book = mybook.books.find({"author_ids":id})
        else:
            logger.info(f"Limit query argument is given as {str(limit)}")
            logger.info(f"Checking if any book found under the loggedin author")
            get_book=mybook.books.find({"author_ids": id}).limit(limit)
        if get_book.count()==0:
            logger.error(f"No books found under the loggedin author")
            logger.info(f"Get All Book Request Finished")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No Books found!")
        logger.info(f"Books found in DB")
        logger.info(f"Get All Book Request Finished")
        return json.loads(json_util.dumps(get_book))
    else:
        logger.info(f"Received request with search query argument as {search}")
        mybook.books.create_index([("title","text")])
        if not limit:
            logger.info(f"Checking in DB with the search argument provided")
            result = mybook.books.find({"$and":[{"author_ids": id},{"$text":{"$search":search}}]})
        else:
            logger.info(f"Limit query argument is given as {str(limit)}")
            logger.info(f"Checking in DB with the search and limit arguments provided")
            result = mybook.books.find({"$and": [{"author_ids": id}, {"$text": {"$search": search}}]}).limit(limit)
        if result == None or result.count()==0:
            logger.error("No books found")
            logger.info(f"Get All Book Request Finished")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No books found!")
        logger.info(f"Record Found in DB")
        logger.info(f"Get All Book Request Finished")
        return json.loads(json_util.dumps(result))

def show_by_title(title: str,conn):
    logger.info(f"Get All Book Request with title {title} received!")
    mybook=conn["BookDB"]
    logger.info(f"Checking in books collection with this title")
    get_book = mybook.books.find_one({"title": title})
    if get_book== None:
        logger.error(f"No Books found under this title '{title}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this title '{title}'")
    logger.info(f"Books found in DB is {get_book}")
    logger.info(f"Get All Book Request with title {title} Finished!")
    return json.loads(json_util.dumps(get_book))

def patch(id:str, request: bookmodel.UpdateBook, current_user_id:str,conn):
    logger.info(f"Update Book Request received for book id {id}")
    mybook=conn["BookDB"]
    logger.info(f"Checking in books collection with this book id {id}")
    if mybook.books.find({"$and":[{"_id": ObjectId(id)},{"author_ids":current_user_id}]}).count()==0:
        logger.error(f"No Books found under this Author with this book id '{id}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No Books found under this Author with this book id '{id}'")
    logger.info(f"Books exists with this id {id}")
    body = request.model_dump(exclude_unset=True)
    logger.info(f"Request body received is {body}")
    if body=={}:
        logger.error(f"Request body found empty")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Nothing updated! Please update atleast one field")
    if "title" in body:
        check_book_title = mybook.books.find_one({"title":body["title"]})
        if check_book_title:
            logger.error(f"The title {body['title']} is already present in DB. Hence rejecting the request.")
            logger.info(f"Update Book Request for book id {id} finished")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="The title is already taken!. Please change the title and then retry!")
    updated_book_detail = mybook.books.update({"_id": ObjectId(id)},{"$set":body})
    logger.info(f"Successfully updated the books collection")
    updated_book_detail=mybook.books.find_one({"_id":ObjectId(id)})
    for key,value in body.items():
        update_book_field_in_authors=mybook.authors.update_many({"books._id":ObjectId(id)},{ "$set": {f"books.$.{key}":value}})
    logger.info(f"Successfully updated the authors collection also")
    logger.info(f"Update Book Request for book id {id} finished")
    return json.loads(json_util.dumps(updated_book_detail))

def delete(id: str, current_user_id:str,conn):
    logger.info(f"Delete Book Request received for book id {id}")
    mybook=conn["BookDB"]
    logger.info(f"Checking in books collection db if any book id {id} is present in DB")
    delete_book= mybook.books.find_one_and_delete({"_id": ObjectId(id), "author_ids": current_user_id})
    if delete_book == None:
        logger.error(f"No books found with this book id {id} in DB. Hence rejecting this request.")
        logger.info(f"Delete Book Request for book id {id} finished")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Incorrect ID provided. Please retry again with the correct id")
    logger.info(f"Book Found wiht this book id {id} and successfully deleted from books collection")
    delete_book_from_authors_collection = mybook.authors.update_many({"books._id":ObjectId(id)},{ "$pull": { "books": { "_id": ObjectId(id) } }})
    logger.info(f"Successfully deleted from authors collection also")
    logger.info(f"Delete Book Request for book id {id} finished")

