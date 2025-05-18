import logging
from typing import Optional, Dict, Any
import time
from src.db.schemas.models import ModelUsage, User, Chat
from src.db.init_db import session_factory
from datetime import datetime
import tiktoken
from src.routes.analytics_routes import handle_new_model_usage
import asyncio

from src.utils.logger import Logger
from src.utils.model_registry import get_provider_for_model, calculate_cost

logger = Logger(name="ai_manager", see_time=True, console_log=True)

class AI_Manager:
    """Manages AI model interactions and usage tracking"""
    
    def __init__(self):
        self.tokenizer = None
        # Initialize tokenizer - could use tiktoken or another tokenizer
        try:
            import tiktoken
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            logger.log_message("Tiktoken not available, using simple tokenizer", level=logging.WARNING)
            self.tokenizer = SimpleTokenizer()
            
    def save_usage_to_db(self, user_id, chat_id, model_name, provider, 
                       prompt_tokens, completion_tokens, total_tokens,
                       query_size, response_size, cost, request_time_ms, 
                       is_streaming=False):
        """Save model usage data to the database"""
        try:
            session = session_factory()
            
            # Verify user_id exists or is None (which is allowed by the foreign key constraint)
            if user_id is not None:
                user_exists = session.query(session.query(User).filter_by(user_id=user_id).exists()).scalar()
                if not user_exists:
                    logger.log_message(f"User ID {user_id} does not exist, setting to None", level=logging.WARNING)
                    user_id = None
            
            # Verify chat_id exists or is None (which is allowed by the foreign key constraint)
            if chat_id is not None:
                chat_exists = session.query(session.query(Chat).filter_by(chat_id=chat_id).exists()).scalar()
                if not chat_exists:
                    logger.log_message(f"Chat ID {chat_id} does not exist, setting to None", level=logging.WARNING)
                    chat_id = None
            
            # Create usage record
            usage = ModelUsage(
                user_id=user_id,
                chat_id=chat_id,
                model_name=model_name,
                provider=provider,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                query_size=query_size,
                response_size=response_size,
                cost=cost,
                timestamp=datetime.utcnow(),
                is_streaming=is_streaming,
                request_time_ms=request_time_ms
            )
            
            session.add(usage)
            session.commit()
            
            # Broadcast the event asynchronously
            asyncio.create_task(handle_new_model_usage(usage))
            
        except Exception as e:
            session.rollback()
            logger.log_message(f"Error saving usage data to database for chat {chat_id}: {str(e)}", level=logging.ERROR)
        finally:
            session.close()
        
    def calculate_cost(self, model_name, input_tokens, output_tokens):
        """Calculate the cost for using the model based on tokens"""
        if not model_name:
            return 0
        
        # Get provider for logging
        model_provider = get_provider_for_model(model_name)    
        logger.log_message(f"[> ] Model Name: {model_name}, Model Provider: {model_provider}", level=logging.INFO)
        
        # Use the centralized calculate_cost function
        return calculate_cost(model_name, input_tokens, output_tokens)

    def get_provider_for_model(self, model_name):
        """Determine the provider based on model name"""
        # Use the centralized get_provider_for_model function
        return get_provider_for_model(model_name)

class SimpleTokenizer:
    """A very simple tokenizer implementation for fallback"""
    def encode(self, text):
        return len(text.split())
