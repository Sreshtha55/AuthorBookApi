from fastapi import FastAPI,Request,Response,status
import models
from config.db import conn
from routes import book, author, authentication
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(authentication.router)
app.include_router(book.router)
app.include_router(author.router)

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


@app.middleware("http")
async def time_in_header(request:Request,call_next):
    start_time=time.time()
    response = await call_next(request)
    try:
        total_time = time.time() - start_time
        response.headers["X-time-taken"] = str(total_time)
        return response
    except RuntimeError as exc:
        if str(exc) == 'No response returned.' and await request.is_disconnected():
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise


