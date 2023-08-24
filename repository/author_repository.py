from models import bookmodel
# from config.db import validate_db
from fastapi.exceptions import HTTPException
from fastapi import status,Depends,Request
from fastapi.responses import JSONResponse
from security.hashing import Hash
from fastapi.encoders import jsonable_encoder
import pydantic
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


def create_author(req,request: bookmodel.Author,conn):
    mybook = conn["BookDB"]
    record = request.model_dump(exclude_unset=True)
    logger.info(f"Create Author Request received!")
    logger.info(f"Request body received is {record}")
    logger.info(f"Checking whether the email is already present in db or not")
    if mybook.authors.find_one({"email": record["email"]}):
        logger.error("Email already registered. Hence sending 400 response code")
        logger.info(f"Create Author Request Finished")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You are already registered, either register with a different email or please login with your registered email . If wants to change password then please use endpoint {str(req.url._url)+'author/password_change'}")
    logger.info("Encrypting password")
    record.update({"password": Hash.bcrypt(request.password)})
    logger.info("Password encypted!")
    new_author = mybook.authors.insert_one(record)
    logger.info("Record inserted into authors collection")
    inserted_author = mybook.authors.find_one({"email": request.email}, {"password":0})
    logger.info(f"Returning response as {inserted_author} in json")
    logger.info(f"Create Author Request Finished")
    return json.loads(json_util.dumps(inserted_author))

def change_password(body: bookmodel.ChangePassword,email:str,conn):
    mybook = conn["BookDB"]
    record = body.model_dump()
    logger.info("Change Password Request received!")
    # print(Hash.bcrypt(record["current_password"]))
    # print(mybook.authors.find_one({"email": current_user.email},{"password":1})["password"])
    logger.info("Matching the current Password given from DB")
    if Hash.verify(mybook.authors.find_one({"email": email},{"password":1})["password"],record["current_password"]):
        logger.info("Password Matched now checking if the new password is the same as the current password")
        if record["current_password"]==record["new_password"]:
            logger.error("Current Password and New Password matched!")
            logger.info("Change Password Request Finshed")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"The new password matches with the current password. So please set different password! ")
        get_author = mybook.authors.find_one_and_update({"email": email}, {"$set": {"password": Hash.bcrypt(record["new_password"])}})
    else:
        logger.error(" Wrong Current Password provided!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Wrong current password provided! ")
    logger.info("Password Successfully Changed!")
    logger.info("Change Password Request Finshed")
    return JSONResponse({"detail": "Your password has been updated successfully"})
    # return JSONResponse(content="Your password has been updated successfully")

def show(email:str,conn):
    mybook = conn["BookDB"]
    logger.info(f"Get request received to show loggedin author details")
    logger.info(f"Checking the loggedin email {email} in Database")
    authors = mybook.authors.find_one({"email": email})
    if authors == None:
        logger.error(f"Email not found in Database!")
        logger.info(f"Get request call Finshed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"The email {email} is not found!")
    logger.info(f"Author details found is {authors}")
    logger.info(f"Get request call Finshed")
    return json.loads(json_util.dumps(authors))

def profile(email:str,conn):
    mybook = conn["BookDB"]
    logger.info(f"Get request received to show author profile using email id")
    logger.info(f"Checking the email {email} provided in Database")
    record= mybook.authors.find_one({"email":email},{"password":0})
    if record == None:
        logger.error(f"Email not found in Database!")
        logger.info(f"Get request to show author profile using email id Finished")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No Author found with email {email} given.")
    logger.info(f"Author details found is {record}")
    logger.info(f"Get request to show author profile using email id Finished")
    return json.loads(json_util.dumps(record))

def patch(request: bookmodel.UpdateAuthor, email:str,conn):
    mybook = conn["BookDB"]
    logger.info(f"Update request received to update loggedin author {email} profile")
    # if not mybook.authors.find_one({"$and": [{"_id": ObjectId(id)}, {"email": current_user.email}]}):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                         detail=f"Invalid id {id} given.")
    body = request.model_dump(exclude_unset=True)
    logger.info(f"Request body received is {body}")
    if body=={}:
        logger.error(f"Request body received is empty!")
        logger.info(f"Update request to update loggedin author {email} profile Finished")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Nothing updated! Please update atleast one field")
    if "email" in body:
        find_email = mybook.authors.find_one({"email":body["email"]})
        if find_email:
            logger.error(f"The email {body['email']} is already present in DB. Hence rejecting this update request.")
            logger.info(f"Update request to update loggedin author {email} profile Finished")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email is already taken. Please retry with another email!")     
        authors_update = mybook.authors.update_one({"email": email}, {"$set": body})
        logger.info(f"Record updated in DB")
        authors = mybook.authors.find_one({"_id":authors_update["_id"]})
        logger.info(f"Updated record is {authors}")
        logger.info(f"Update request to update loggedin author {email} profile Finished")
        return json.loads(json_util.dumps(authors))                       
    logger.info(f"No email found in the request body")   
    authors_update = mybook.authors.find_one_and_update({"email": email}, {"$set": body})
    logger.info(f"Record updated in DB")
    authors = mybook.authors.find_one({"_id":authors_update["_id"]})
    logger.info(f"Updated record is {authors}")
    logger.info(f"Update request to update loggedin author {email} profile Finished")
    return json.loads(json_util.dumps(authors))