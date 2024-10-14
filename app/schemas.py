from pydantic import BaseModel


class Message(BaseModel):
    room: int
    message: str
