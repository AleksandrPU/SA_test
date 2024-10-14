from fastapi import Request, Response, status
from fastapi.responses import JSONResponse


def invalid_status_exception_handler(
    request: Request, exc: Exception
) -> Response:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": str(exc)},
    )
