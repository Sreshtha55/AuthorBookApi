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

# pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str


def create_author(req,request: bookmodel.Author,conn):
    mybook = conn["BookDB"]
    record = request.model_dump(exclude_unset=True)
    new_body = {
        key: value for key, value in record.items()
        if value is not None
    }
    if mybook.authors.find_one({"email": new_body["email"]}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You are already registered, either register with a different email or please login with your registered email . If wants to change password then please use endpoint {str(req.url._url)+'author/password_change'}")
    record.update({"password": Hash.bcrypt(request.password)})
    new_author = mybook.authors.insert_one(record)
    inserted_author = mybook.authors.find_one({"email": request.email}, {"password":0})
    return json.loads(json_util.dumps(inserted_author))

def change_password(body: bookmodel.ChangePassword,email:str,conn):
    mybook = conn["BookDB"]
    record = body.model_dump()
    # print(Hash.bcrypt(record["current_password"]))
    # print(mybook.authors.find_one({"email": current_user.email},{"password":1})["password"])
    if Hash.verify(mybook.authors.find_one({"email": email},{"password":1})["password"],record["current_password"]):
        if record["current_password"]==record["new_password"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"The new password matches with the current password. So please set different password! ")
        get_author = mybook.authors.find_one_and_update({"email": email}, {"$set": {"password": Hash.bcrypt(record["new_password"])}})
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Wrong current password provided! ")
    return JSONResponse({"detail": "Your password has been updated successfully"})
    # return JSONResponse(content="Your password has been updated successfully")

def show(email:str,conn):
    mybook = conn["BookDB"]
    authors = mybook.authors.find_one({"email": email})
    return json.loads(json_util.dumps(authors))

def profile(email:str,conn):
    mybook = conn["BookDB"]
    record= mybook.authors.find_one({"email":email},{"password":0})
    if record == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No Author found with email {email} given.")
    return json.loads(json_util.dumps(record))

def patch(request: bookmodel.UpdateAuthor, email:str,conn):
    mybook = conn["BookDB"]
    # if not mybook.authors.find_one({"$and": [{"_id": ObjectId(id)}, {"email": current_user.email}]}):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                         detail=f"Invalid id {id} given.")
    body = request.model_dump(exclude_unset=True)
    if body=={}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Nothing updated! Please update atleast one field")
    if "email" in body:
        find_email = mybook.authors.find_one({"email":email})
        if find_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email is already taken. Please retry with another email!")                               
    authors_update = mybook.authors.find_one_and_update({"email": email}, {"$set": body})
    authors = mybook.authors.find_one({"_id":authors_update["_id"]})
    return json.loads(json_util.dumps(authors))