from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.utils.logger.logger import Logger

logger = Logger()


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"},
    )
