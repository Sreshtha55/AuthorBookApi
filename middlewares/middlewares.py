import json

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request,HTTPException,status,Response
from config.db import validate_db
import time

class DBCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        conn = validate_db()
        try:
            conn.admin.command('ping')
            request.headers.__dict__["_list"].append(
                ("db-status".encode(),"UP".encode())
            )
        except Exception:
            request.headers.__dict__["_list"].append(
                ("db-status".encode(),"Down".encode())
            )
        
        response = await call_next(request)
        
        return response
    

class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request,call_next):
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

