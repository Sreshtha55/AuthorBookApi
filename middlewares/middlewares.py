import json

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request,HTTPException,status,Response
from config.db import validate_db
import time
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


class DBCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        conn = validate_db()
        try:
            logger.info("...............Checking DB Status...........")
            conn.admin.command('ping')
            logger.info("...............DB Checking Done...........")
            request.headers.__dict__["_list"].append(
                ("db-status".encode(),"UP".encode())
            )
            logger.info("DB is Up. Hence adding DB status Up in every api call request headers.")
        except Exception as e:
            request.headers.__dict__["_list"].append(
                ("db-status".encode(),"Down".encode())
            )
            logger.error("DB is down. Hence adding DB status Down in every api call request headers.")
            logger.exception("DB Error: " + str(e))
        response = await call_next(request)
        
        return response
    

class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request,call_next):
        start_time=time.time()
        response = await call_next(request)
        try:
            total_time = time.time() - start_time
            response.headers["X-time-taken"] = str(total_time)
            logger.info(f"Response took {str(total_time)}secs to respond. Added in the response header")
            return response
        except RuntimeError as exc:
            if str(exc) == 'No response returned.' and await request.is_disconnected():
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            raise

