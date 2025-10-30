import asyncio
import logging
from typing import Dict

from asyncpg import PostgresError
from fastapi import status
from fastapi.responses import JSONResponse

from app.database.database_calls import postgres_database
from app.models.history.events_output_model import DatabaseEventTable
from app.models.history.history_response_model import (
    HistoryAPIResponse,
    HistoryResponseStatusCode,
)
from app.utils.logger.logger import Logger

logger = Logger()


async def history_events_service(conversation_id: str) -> Dict | JSONResponse:
    try:
        history_events = await postgres_database.get_events_by_conversation_id(
            conversation_id
        )
    except (TimeoutError, asyncio.TimeoutError) as exception:
        logger.log(
            "Timeout error while fetching events from database",
            level=logging.ERROR,
            conversation_id=conversation_id,
            payload=exception,
        )
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR,
                error_message="Query timed out while fetching events from database",
            ).convert_to_error_response(),
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except PostgresError as exception:
        logger.log(
            "Database error while fetching events from database",
            level=logging.ERROR,
            conversation_id=conversation_id,
            payload=exception,
        )
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR,
                error_message="Database error fetching events from database",
            ).convert_to_error_response(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as exception:
        logger.log(
            "Unexpected error while fetching events from database",
            level=logging.ERROR,
            conversation_id=conversation_id,
            payload=exception,
        )
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR,
                error_message="Unexpected error fetching events from database",
            ).convert_to_error_response(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not history_events:
        return JSONResponse(
            content=HistoryAPIResponse(
                status=HistoryResponseStatusCode.ERROR,
                error_message="Conversation ID not found",
            ).convert_to_error_response(),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    parsed_events = [DatabaseEventTable(**event) for event in history_events]

    return HistoryAPIResponse(
        status=HistoryResponseStatusCode.SUCCESS, data=parsed_events
    ).convert_to_success_response()
