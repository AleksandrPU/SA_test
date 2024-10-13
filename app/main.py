from fastapi import (
    Depends,
    FastAPI,
    Request,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from faststream.rabbit.fastapi import Logger, RabbitRouter
from pydantic import BaseModel
from websockets import InvalidStatus
from websockets.asyncio.client import connect

from app.exceptions import token_empty_exception_handler

router = RabbitRouter("amqp://guest:guest@localhost:5672/")

app = FastAPI()
app.add_exception_handler(InvalidStatus, handler=token_empty_exception_handler)


class Message(BaseModel):
    room: int
    message: str


def call() -> bool:
    return True


async def get_token(
    websocket: WebSocket,
    logger: Logger,
    token: str | None = None,
) -> str:
    if token is None:
        message = "Token is empty"
        logger.error(message)
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason=message
        )
    return token


@router.post("/post_message/")
async def post_messages(
    message: Message,
    request: Request,
    logger: Logger,
    token: str | None = None,
):
    async with connect(
        f"ws://{request.url.netloc}/updates/{message.room}"
        f"{'?token=' + token if token else ''}"
    ) as ws:
        logger.debug(f"Post message: {message}")
        await ws.send(message.message)


@router.websocket("/updates/{room_id}")
async def get_updates(
    websocket: WebSocket,
    room_id: int,
    logger: Logger,
    token: str = Depends(get_token),
):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await router.broker.publisher().publish(
                {"message": data}, str(room_id)
            )
    except WebSocketDisconnect:
        logger.debug("Client disconnected")
    except Exception as error:
        logger.error(error)


app.include_router(router)
