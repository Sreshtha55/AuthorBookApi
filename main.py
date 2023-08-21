from fastapi import FastAPI,Request,Response,status
import models
from routes import book, author, authentication
import time
from fastapi.middleware.cors import CORSMiddleware
from middlewares.middlewares import DBCheckMiddleware,ResponseTimeMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PATCH", "PUT", "DELETE"],
	allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(DBCheckMiddleware)
app.add_middleware(ResponseTimeMiddleware)


app.include_router(authentication.router)
app.include_router(book.router)
app.include_router(author.router)


