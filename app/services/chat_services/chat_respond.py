from fastapi import HTTPException, status

from app.database.helpers import (
    log_chatbot_response_interaction,
    log_user_message_interaction,
)
from app.models.chat.chat_message_input_model import ChatMessage
from app.models.chat.chat_message_output_model import (
    ConversationMessages,
    ConversationMessagesOutput,
    HandoffDetails,
    OutputRole,
)
from app.models.handler_config_model import HandlerConfigModel
from app.models.handler_response_model import HandlerResponse, HandlerResponseStatus
from app.models.redis_messages_model import RedisMessages
from app.redis_services.redis_methods import (
    generate_new_part_ids,
    get_conversation_id,
    push_message_to_redis,
)
from app.router.chatbot_router import ChatbotRouter
from app.utils.logger.logger import Logger

logger = Logger()
chatbot_router = ChatbotRouter()


async def chat_service(
    request: ChatMessage,
) -> ConversationMessagesOutput | HTTPException:
    user_id = request.user_id
    conversation_id = await get_conversation_id(user_id)

    if not conversation_id:
        logger.log("User has no active conversations", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer has no active conversations",
        )

    await generate_new_part_ids(user_id)

    await process_user_message(user_id, request, conversation_id)

    handler_response: HandlerResponse = await chatbot_router.route(
        request, HandlerConfigModel(user_id=user_id, conversation_id=conversation_id)
    )

    await process_chatbot_response(user_id, conversation_id, handler_response)

    return ConversationMessagesOutput(
        conversation_id=conversation_id,
        message=ConversationMessages(
            role=OutputRole.ASSISTANT, content=handler_response.message
        ),
        handoff=HandoffDetails(
            should_handoff=handler_response.status
            == HandlerResponseStatus.SUPPORT_HANDOFF
        ),
    )


async def process_user_message(
    user_id: str, message: ChatMessage, conversation_id: str
) -> None:
    await push_message_to_redis(
        user_id=user_id,
        conversation_id=conversation_id,
        message=RedisMessages(role=message.role, content=message.content),
    )
    await log_user_message_interaction(user_id, conversation_id, message)


async def process_chatbot_response(
    user_id: str, conversation_id: str, handler_response: HandlerResponse
) -> None:
    await push_message_to_redis(
        user_id=user_id,
        conversation_id=conversation_id,
        message=RedisMessages(
            role=OutputRole.ASSISTANT, content=handler_response.message
        ),
    )
    await log_chatbot_response_interaction(user_id, conversation_id, handler_response)
