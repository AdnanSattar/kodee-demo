from app.handlers.domains.domain_handler import DomainChatHandler
from app.handlers.out_of_scope.out_of_scope_handler import OutOfScopeChatHandler
from app.models.chat.chat_message_input_model import ChatbotLabel, ChatMessage
from app.models.chat.chat_message_output_model import OutputChatbotLabel
from app.models.handler_config_model import HandlerConfigModel
from app.models.handler_response_model import HandlerResponse, HandlerResponseStatus
from app.router.gpt_chatbot_label import generate_chatbot_label
from app.router.support_handoff_decider import (
    get_handoff_response_message,
    is_seeking_human_assistance,
)
from app.utils.logger.logger import Logger

logger = Logger()


class ChatbotRouter:
    def __init__(self):
        logger.log("ChatbotRouter initialized", level="INFO")
        self.handler_classes = {
            ChatbotLabel.DOMAIN: DomainChatHandler,
            ChatbotLabel.OUT_OF_SCOPE: OutOfScopeChatHandler,
        }

        self.chatbot_label_mapping = {
            ChatbotLabel.DOMAIN: OutputChatbotLabel.DOMAIN_BOT,
            ChatbotLabel.OUT_OF_SCOPE: OutputChatbotLabel.OUT_OF_SCOPE_BOT,
        }

    async def route(
        self, message: ChatMessage, handler_config: HandlerConfigModel
    ) -> HandlerResponse:
        logger.log(f"Routing message with label: {message.chatbot_label}", level="INFO")
        if await is_seeking_human_assistance(
            handler_config.conversation_id, handler_config.user_id
        ):
            logger.log("Support handoff triggered", level="INFO")
            return HandlerResponse(
                status=HandlerResponseStatus.SUPPORT_HANDOFF,
                message=await get_handoff_response_message(
                    handler_config.conversation_id, handler_config.user_id
                ),
                chatbot_label=OutputChatbotLabel.SUPPORT_HANDOFF_BOT,
            )

        message.chatbot_label = await generate_chatbot_label(
            handler_config.conversation_id, handler_config.user_id
        )
        logger.log(f"Generated chatbot label: {message.chatbot_label}", level="INFO")

        handler_class = self.handler_classes.get(message.chatbot_label)
        response = await handler_class(handler_config).handle(message)
        response.chatbot_label = self.chatbot_label_mapping.get(message.chatbot_label)
        logger.log(
            f"Handled message with label: {response.chatbot_label}", level="INFO"
        )
        return response
