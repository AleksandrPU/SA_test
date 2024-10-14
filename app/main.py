from fastapi import FastAPI
from websockets import InvalidStatusCode

from app.exceptions import invalid_status_exception_handler
from app.routers import router

app = FastAPI()
app.include_router(router)
app.add_exception_handler(
    InvalidStatusCode, handler=invalid_status_exception_handler
)
