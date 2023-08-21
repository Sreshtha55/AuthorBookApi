from fastapi import APIRouter,Depends,status,Request,HTTPException
from security import oauth2
from models import bookmodel
from pydantic import EmailStr
from repository import author_repository
from config.db import validate_db

router = APIRouter(prefix="/author", tags=['Author'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(req:Request,request: bookmodel.Author,conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    return author_repository.create_author(req,request,conn)


@router.put('/password_change',status_code=status.HTTP_200_OK)
def change_password(req:Request,body: bookmodel.ChangePassword, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    if req.headers.get("db-status") == "Down":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Down")
    current_user_email=current_user.email
    return author_repository.change_password(body,current_user_email,conn)


@router.get('/me', response_model=bookmodel.ShowAuthor, status_code=status.HTTP_200_OK, response_model_exclude_unset=True)
def show(current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    current_user_email = current_user.email
    return author_repository.show(current_user_email,conn)

@router.get('/profile/{email}',response_model=bookmodel.AuthorBooks,status_code=status.HTTP_200_OK)
def profile(email:EmailStr, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    return author_repository.profile(email,conn)


@router.patch('/me',response_model=bookmodel.UpdateAuthor,status_code=status.HTTP_200_OK)
def patch(request: bookmodel.UpdateAuthor, current_user: bookmodel.Author = Depends(oauth2.get_current_user),conn=Depends(validate_db)):
    current_user_email = current_user.email
    return author_repository.patch(request,current_user_email,conn)

