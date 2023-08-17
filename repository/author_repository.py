from models import bookmodel
from config.db import conn
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.responses import JSONResponse
from security.hashing import Hash
from schemas import *

def create_author(request: bookmodel.Author):
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
    return DictSerializer(inserted_author)

def change_password(body: bookmodel.ChangePassword,email:str):
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
    return JSONResponse(content="Your password has been updated successfully")

def show(email:str):
    mybook = conn["BookDB"]
    authors = mybook.authors.find_one({"email": email})
    return DictSerializer(authors)

def profile(email:str):
    mybook = conn["BookDB"]
    record= mybook.authors.find_one({"email":email},{"password":0})
    if record == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No Author found with email {email} given.")
    return record

def patch(request: bookmodel.UpdateAuthor, email:str):
    mybook = conn["BookDB"]
    # if not mybook.authors.find_one({"$and": [{"_id": ObjectId(id)}, {"email": current_user.email}]}):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                         detail=f"Invalid id {id} given.")
    body = request.model_dump(exclude_unset=True)
    if body=={}:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Nothing updated! Please update atleast one field")
    new_body = {
        key: value for key, value in body.items()
        if value is not None
    }
    authors = mybook.authors.find_one_and_update({"email": email}, {"$set": new_body})
    return JSONResponse(content="Successfully Updated!")