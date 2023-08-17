from fastapi import APIRouter,Depends,status
from security import oauth2
from models import bookmodel
from pydantic import EmailStr
from repository import author_repository

router = APIRouter(prefix="/author", tags=['Author'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request: bookmodel.Author):
    return author_repository.create_author(request)


@router.put('/password_change',status_code=status.HTTP_200_OK)
def change_password(body: bookmodel.ChangePassword, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    current_user_email=current_user.email
    return author_repository.change_password(body,current_user_email)


@router.get('/me', response_model=bookmodel.ShowAuthor, status_code=status.HTTP_200_OK, response_model_exclude_unset=True)
def show(current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    current_user_email = current_user.email
    return author_repository.show(current_user_email)

@router.get('/profile/{email}',response_model=bookmodel.AuthorBooks,status_code=status.HTTP_200_OK)
def profile(email:EmailStr, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    author_repository.profile(email)


@router.patch('/me')
def patch(request: bookmodel.UpdateAuthor, current_user: bookmodel.Author = Depends(oauth2.get_current_user)):
    current_user_email = current_user.email
    return author_repository.patch(request,current_user_email)

