# Standard library imports
import asyncio
import json
import logging
import os
import time
import uuid
from io import StringIO
from typing import List, Optional

# Third-party imports
import groq
import pandas as pd
import uvicorn
import requests
from dotenv import load_dotenv
from fastapi import (
    Depends, 
    FastAPI, 
    File, 
    Form, 
    HTTPException, 
    Request, 
    UploadFile
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from llama_index.core import Document, VectorStoreIndex
from pydantic import BaseModel

# Local application imports
from scripts.format_response import format_response_to_markdown
from src.agents.agents import *
from src.agents.retrievers.retrievers import *
from src.managers.ai_manager import AI_Manager
from src.managers.session_manager import SessionManager
from src.routes.analytics_routes import router as analytics_router
from src.routes.automotive_routes import router as automotive_router
from src.routes.chat_routes import router as chat_router
from src.routes.code_routes import router as code_router
from src.routes.session_routes import router as session_router, get_session_id_dependency
from src.schemas.query_schemas import QueryRequest
from src.utils.logger import Logger

# File server configuration
FILE_SERVER_URL = os.getenv("FILE_SERVER_URL", "http://localhost:8001")

# In-memory cache for loaded datasets
datasets_cache = {}

logger = Logger("app", see_time=True, console_log=False)
load_dotenv()

styling_instructions = [
    """
        Dont ignore any of these instructions.
        For a line chart always use plotly_white template, reduce x axes & y axes line to 0.2 & x & y grid width to 1. 
        Always give a title and make bold using html tag axis label and try to use multiple colors if more than one line
        Annotate the min and max of the line
        Display numbers in thousand(K) or Million(M) if larger than 1000/100000 
        Show percentages in 2 decimal points with '%' sign
        Default size of chart should be height =1200 and width =1000
        
        """
        
   , """
        Dont ignore any of these instructions.
        For a bar chart always use plotly_white template, reduce x axes & y axes line to 0.2 & x & y grid width to 1. 
        Always give a title and make bold using html tag axis label 
        Always display numbers in thousand(K) or Million(M) if larger than 1000/100000. 
        Annotate the values of the bar chart
        If variable is a percentage show in 2 decimal points with '%' sign.
        Default size of chart should be height =1200 and width =1000
        """
        ,

          """
        For a histogram chart choose a bin_size of 50
        Do not ignore any of these instructions
        always use plotly_white template, reduce x & y axes line to 0.2 & x & y grid width to 1. 
        Always give a title and make bold using html tag axis label 
        Always display numbers in thousand(K) or Million(M) if larger than 1000/100000. Add annotations x values
        If variable is a percentage show in 2 decimal points with '%'
        Default size of chart should be height =1200 and width =1000
        """,


          """
        For a pie chart only show top 10 categories, bundle rest as others
        Do not ignore any of these instructions
        always use plotly_white template, reduce x & y axes line to 0.2 & x & y grid width to 1. 
        Always give a title and make bold using html tag axis label 
        Always display numbers in thousand(K) or Million(M) if larger than 1000/100000. Add annotations x values
        If variable is a percentage show in 2 decimal points with '%'
        Default size of chart should be height =1200 and width =1000
        """,

          """
        Do not ignore any of these instructions
        always use plotly_white template, reduce x & y axes line to 0.2 & x & y grid width to 1. 
        Always give a title and make bold using html tag axis label 
        Always display numbers in thousand(K) or Million(M) if larger than 1000/100000. Add annotations x values
        Dont add K/M if number already in , or value is not a number
        If variable is a percentage show in 2 decimal points with '%'
        Default size of chart should be height =1200 and width =1000
        """,
"""
    For a heat map
    Use the 'plotly_white' template for a clean, white background. 
    Set a chart title 
    Style the X-axis with a black line color, 0.2 line width, 1 grid width, format 1000/1000000 as K/M
    Do not format non-numerical numbers 
    .style the Y-axis with a black line color, 0.2 line width, 1 grid width format 1000/1000000 as K/M
    Do not format non-numerical numbers 

    . Set the figure dimensions to a height of 1200 pixels and a width of 1000 pixels.
""",
"""
    For a Histogram, used for returns/distribution plotting
    Use the 'plotly_white' template for a clean, white background. 
    Set a chart title 
    Style the X-axis  1 grid width, format 1000/1000000 as K/M
    Do not format non-numerical numbers 
    .style the Y-axis, 1 grid width format 1000/1000000 as K/M
    Do not format non-numerical numbers 
    
    Use an opacity of 0.75

     Set the figure dimensions to a height of 1200 pixels and a width of 1000 pixels.
"""
]

# Add near the top of the file, after imports
DEFAULT_MODEL_CONFIG = {
    "provider": os.getenv("MODEL_PROVIDER", "openai"),
    "model": os.getenv("MODEL_NAME", "gpt-4o-mini"),
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": float(os.getenv("TEMPERATURE", 1.0)),
    "max_tokens": int(os.getenv("MAX_TOKENS", 6000))
}

# Create default LM config but don't set it globally
if DEFAULT_MODEL_CONFIG["provider"].lower() == "groq":
    default_lm = dspy.GROQ(
        model=DEFAULT_MODEL_CONFIG["model"],
        api_key=DEFAULT_MODEL_CONFIG["api_key"],
        temperature=DEFAULT_MODEL_CONFIG["temperature"],
        max_tokens=DEFAULT_MODEL_CONFIG["max_tokens"]
    )
elif DEFAULT_MODEL_CONFIG["provider"].lower() == "gemini":
    default_lm = dspy.LM(
        model=f"gemini/{DEFAULT_MODEL_CONFIG['model']}",
        api_key=DEFAULT_MODEL_CONFIG["api_key"],
        temperature=DEFAULT_MODEL_CONFIG["temperature"],
        max_tokens=DEFAULT_MODEL_CONFIG["max_tokens"]
    )
else:
    default_lm = dspy.LM(
        model=DEFAULT_MODEL_CONFIG["model"],
        api_key=DEFAULT_MODEL_CONFIG["api_key"],
        temperature=DEFAULT_MODEL_CONFIG["temperature"],
        max_tokens=DEFAULT_MODEL_CONFIG["max_tokens"]
    )

# Function to get model config from session or use default
def get_session_lm(session_state):
    """Get the appropriate LM instance for a session, or default if not configured"""
    # Define a fallback LM creator that ensures all required attributes
    def create_fallback_lm():
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Use environment variables with fallbacks
        provider = os.getenv("MODEL_PROVIDER", "gemini").lower()
        model = os.getenv("MODEL_NAME", "gemini-1.5-pro")
        api_key = None
        
        # Get appropriate API key based on provider
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
        else:  # Default to OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
        
        temperature = float(os.getenv("TEMPERATURE", 0.7))
        max_tokens = int(os.getenv("MAX_TOKENS", 4000))
        
        logger.log_message(f"Creating fallback LM with provider={provider}, model={model}", level=logging.INFO)
        
        # Create appropriate LM based on provider
        try:
            if provider == "groq":
                return dspy.GROQ(
                    model=model,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif provider == "gemini":
                lm = dspy.LM(
                    model=f"gemini/{model}",
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return lm
            elif provider == "anthropic":
                return dspy.LM(
                    model=f"anthropic/{model}",
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                return dspy.LM(
                    model=model,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
        except Exception as e:
            logger.log_message(f"Error creating LM: {str(e)}", level=logging.ERROR)
            # Create a minimal default LM that won't crash
            lm = dspy.LM(
                model="gemini/gemini-1.5-pro",
                api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "missing-api-key",
                temperature=0.7,
                max_tokens=4000
            )
            return lm
    
    # If no session or no model config, use default
    if not session_state or "model_config" not in session_state:
        return create_fallback_lm()
    
    # Get model config from session
    model_config = session_state["model_config"]
    
    # Validate model config has required fields
    required_fields = ["provider", "model", "api_key", "temperature", "max_tokens"]
    if not all(field in model_config for field in required_fields):
        logger.log_message("Model config missing required fields, using fallback", level=logging.WARNING)
        return create_fallback_lm()
    
    # Create LM based on provider
    provider = model_config["provider"].lower()
    try:
        if provider == "groq":
            return dspy.GROQ(
                model=model_config["model"],
                api_key=model_config["api_key"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
        elif provider == "gemini":
            return dspy.LM(
                model=f"gemini/{model_config['model']}",
                api_key=model_config["api_key"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
        elif provider == "anthropic":
            return dspy.LM(
                model=f"anthropic/{model_config['model']}",
                api_key=model_config["api_key"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
        else:
            return dspy.LM(
                model=model_config["model"],
                api_key=model_config["api_key"],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
    except Exception as e:
        logger.log_message(f"Error creating LM from session config: {str(e)}", level=logging.ERROR)
        return create_fallback_lm()

# Initialize retrievers with empty data first
def initialize_retrievers(styling_instructions: List[str], doc: List[str]):
    try:
        style_index = VectorStoreIndex.from_documents([Document(text=x) for x in styling_instructions])
        data_index = VectorStoreIndex.from_documents([Document(text=x) for x in doc])
        return {"style_index": style_index, "dataframe_index": data_index}
    except Exception as e:
        logger.log_message(f"Error initializing retrievers: {str(e)}", level=logging.ERROR)
        raise e

# clear console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


# Check for Housing.csv
housing_csv_path = "Housing.csv"
if not os.path.exists(housing_csv_path):
    logger.log_message(f"Housing.csv not found at {os.path.abspath(housing_csv_path)}", level=logging.ERROR)
    raise FileNotFoundError(f"Housing.csv not found at {os.path.abspath(housing_csv_path)}")

AVAILABLE_AGENTS = {
    "data_viz_agent": data_viz_agent,
    "sk_learn_agent": sk_learn_agent,
    "statistical_analytics_agent": statistical_analytics_agent,
    "preprocessing_agent": preprocessing_agent,
}

PLANNER_AGENTS = {
    "planner_preprocessing_agent": planner_preprocessing_agent,
    "planner_sk_learn_agent": planner_sk_learn_agent,
    "planner_statistical_analytics_agent": planner_statistical_analytics_agent,
    "planner_data_viz_agent": planner_data_viz_agent,
}

# Add session header
X_SESSION_ID = APIKeyHeader(name="X-Session-ID", auto_error=False)

# Update AppState class to use SessionManager
class AppState:
    def __init__(self):
        self._session_manager = SessionManager(styling_instructions, PLANNER_AGENTS)
        self.model_config = DEFAULT_MODEL_CONFIG.copy()
        # Update the SessionManager with the current model_config
        self._session_manager._app_model_config = self.model_config
        self.ai_manager = AI_Manager()
        self.chat_name_agent = chat_history_name_agent
    
    def get_session_state(self, session_id: str):
        """Get or create session-specific state using the SessionManager"""
        return self._session_manager.get_session_state(session_id)

    def clear_session_state(self, session_id: str):
        """Clear session-specific state using the SessionManager"""
        self._session_manager.clear_session_state(session_id)

    def update_session_dataset(self, session_id: str, df, name, desc):
        """Update dataset for a specific session using the SessionManager"""
        self._session_manager.update_session_dataset(session_id, df, name, desc)

    def reset_session_to_default(self, session_id: str):
        """Reset a session to use the default dataset using the SessionManager"""
        self._session_manager.reset_session_to_default(session_id)
    
    def set_session_user(self, session_id: str, user_id: int, chat_id: int = None):
        """Associate a user with a session using the SessionManager"""
        return self._session_manager.set_session_user(session_id, user_id, chat_id)
    
    def get_ai_manager(self):
        """Get the AI Manager instance"""
        return self.ai_manager
    
    def get_provider_for_model(self, model_name):
        return self.ai_manager.get_provider_for_model(model_name)
    
    def calculate_cost(self, model_name, input_tokens, output_tokens):
        return self.ai_manager.calculate_cost(model_name, input_tokens, output_tokens)
    
    def save_usage_to_db(self, user_id, chat_id, model_name, provider, prompt_tokens, completion_tokens, total_tokens, query_size, response_size, cost, request_time_ms, is_streaming=False):
        return self.ai_manager.save_usage_to_db(user_id, chat_id, model_name, provider, prompt_tokens, completion_tokens, total_tokens, query_size, response_size, round(cost, 7), request_time_ms, is_streaming)
    
    def get_tokenizer(self):
        return self.ai_manager.tokenizer
    
    def get_chat_history_name_agent(self):
        return dspy.Predict(self.chat_name_agent)

# Initialize FastAPI app with state
app = FastAPI(title="Auto-Analyst API")
app.state = AppState()

# Configure middleware
# Use a wildcard for local development or read from environment
is_development = os.getenv("ENVIRONMENT", "development").lower() == "development"

allowed_origins = []
frontend_url = os.getenv("FRONTEND_URL", "").strip()
print(f"FRONTEND_URL: {frontend_url}")
if is_development:
    allowed_origins = ["*"]
elif frontend_url:
    allowed_origins = [frontend_url]
else:
    logger.log_message("CORS misconfigured: FRONTEND_URL not set", level=logging.ERROR)
    allowed_origins = []  # or set a default safe origin

# Add a strict origin verification middleware
@app.middleware("http")
async def verify_origin_middleware(request: Request, call_next):
    # Skip origin check in development mode
    if is_development:
        return await call_next(request)
    
    # Get the origin from the request headers
    origin = request.headers.get("origin")
    
    # Log the origin for debugging
    if origin:
        print(f"Request from origin: {origin}")
    
    # If no origin header or origin not in allowed list, reject the request
    if origin and frontend_url and origin != frontend_url:
        print(f"Blocked request from unauthorized origin: {origin}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Not authorized"}
        )
    
    # Continue processing the request if origin is allowed
    return await call_next(request)

# CORS middleware (still needed for browser preflight)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes (for performance)
)

# Add these constants at the top of the file with other imports/constants
RESPONSE_ERROR_INVALID_QUERY = "Please provide a valid query..."
RESPONSE_ERROR_NO_DATASET = "No dataset is currently loaded. Please link a dataset before proceeding with your analysis."
DEFAULT_TOKEN_RATIO = 1.5
REQUEST_TIMEOUT_SECONDS = 60  # Timeout for LLM requests
MAX_RECENT_MESSAGES = 3
DB_BATCH_SIZE = 10  # For future batch DB operations

# Replace the existing chat_with_agent function
@app.post("/chat/{agent_name}", response_model=dict)
async def chat_with_agent(
    agent_name: str, 
    request: QueryRequest,
    request_obj: Request,
    session_id: str = Depends(get_session_id_dependency)
):
    session_state = app.state.get_session_state(session_id)
    
    try:
        # Extract and validate query parameters
        _update_session_from_query_params(request_obj, session_state)
        
        # Check if this is a data analysis request targeting uploaded files
        query = request.query
        if any(keyword in query.lower() for keyword in ["analyze", "dataset", "data", "csv", "file", "files", "uploaded"]):
            # Check for any available file server datasets
            try:
                datasets_response = await get_available_datasets()
                if "files" in datasets_response and datasets_response["files"]:
                    # This seems to be a request about file analysis, forward to analyze-file endpoint
                    logger.log_message(f"Forwarding agent-specific data analysis request to analyze-file: {query}", level=logging.INFO)
                    
                    analysis_request = DataAnalysisRequest(query=query)
                    return await analyze_file(analysis_request, request_obj, session_id)
            except Exception as e:
                logger.log_message(f"Error checking file server datasets: {str(e)}", level=logging.ERROR)
                # Continue with regular processing if file server integration fails
        
        # Validate dataset and agent name
        if session_state["current_df"] is None:
            raise HTTPException(status_code=400, detail=RESPONSE_ERROR_NO_DATASET)

        _validate_agent_name(agent_name)
        
        # Record start time for timing
        start_time = time.time()
        
        # Get chat context and prepare query
        enhanced_query = _prepare_query_with_context(request.query, session_state)
        
        # Initialize agent
        if "," in agent_name:
            agent_list = [AVAILABLE_AGENTS[agent.strip()] for agent in agent_name.split(",")]
            agent = auto_analyst_ind(agents=agent_list, retrievers=session_state["retrievers"])
        else:
            agent = auto_analyst_ind(agents=[AVAILABLE_AGENTS[agent_name]], retrievers=session_state["retrievers"])
        
        # Execute agent with timeout
        try:
            # Get session-specific model
            session_lm = get_session_lm(session_state)
            
            # Use session-specific model for this request
            with dspy.context(lm=session_lm):
                response = await asyncio.wait_for(
                    asyncio.to_thread(agent, enhanced_query, agent_name),
                    timeout=REQUEST_TIMEOUT_SECONDS
                )
        except asyncio.TimeoutError:
            logger.log_message(f"Agent execution timed out for {agent_name}", level=logging.WARNING)
            raise HTTPException(status_code=504, detail="Request timed out. Please try a simpler query.")
        except Exception as agent_error:
            logger.log_message(f"Agent execution failed: {str(agent_error)}", level=logging.ERROR)
            raise HTTPException(status_code=500, detail="Failed to process query. Please try again.")
        
        formatted_response = format_response_to_markdown(response, agent_name, session_state["current_df"])
        
        if formatted_response == RESPONSE_ERROR_INVALID_QUERY:
            return {
                "agent_name": agent_name,
                "query": request.query,
                "response": formatted_response,
                "session_id": session_id
            }
        
        # Track usage statistics
        if session_state.get("user_id"):
            _track_model_usage(
                session_state=session_state,
                enhanced_query=enhanced_query,
                response=response,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        return {
            "agent_name": agent_name,
            "query": request.query,  # Return original query without context
            "response": formatted_response,
            "session_id": session_id
        }
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.log_message(f"Unexpected error in chat_with_agent: {str(e)}", level=logging.ERROR)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
    
    
@app.post("/chat", response_model=dict)
async def chat_with_all(
    request: QueryRequest,
    request_obj: Request,
    session_id: str = Depends(get_session_id_dependency)
):
    session_state = app.state.get_session_state(session_id)

    try:
        # Extract and validate query parameters
        _update_session_from_query_params(request_obj, session_state)
        
        # Check if this is a data analysis request targeting uploaded files
        query = request.query
        if any(keyword in query.lower() for keyword in ["analyze", "dataset", "data", "csv", "file", "files", "uploaded"]):
            # Check for any available file server datasets
            try:
                datasets_response = await get_available_datasets()
                if "files" in datasets_response and datasets_response["files"]:
                    # This seems to be a request about file analysis, forward to analyze-file endpoint
                    logger.log_message(f"Forwarding data analysis request to analyze-file: {query}", level=logging.INFO)
                    
                    analysis_request = DataAnalysisRequest(query=query)
                    return await analyze_file(analysis_request, request_obj, session_id)
            except Exception as e:
                logger.log_message(f"Error checking file server datasets: {str(e)}", level=logging.ERROR)
                # Continue with regular processing if file server integration fails
        
        # Validate dataset
        if session_state["current_df"] is None:
            raise HTTPException(status_code=400, detail=RESPONSE_ERROR_NO_DATASET)
        
        if session_state["ai_system"] is None:
            raise HTTPException(status_code=500, detail="AI system not properly initialized.")

        # Get session-specific model
        session_lm = get_session_lm(session_state)

        # Create streaming response
        return StreamingResponse(
            _generate_streaming_responses(session_state, request.query, session_lm),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'X-Accel-Buffering': 'no'
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.log_message(f"Unexpected error in chat_with_all: {str(e)}", level=logging.ERROR)
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")


# Helper functions to reduce duplication and improve modularity
def _update_session_from_query_params(request_obj: Request, session_state: dict):
    """Extract and validate chat_id and user_id from query parameters"""
    # Check for chat_id in query parameters
    if "chat_id" in request_obj.query_params:
        try:
            chat_id_param = int(request_obj.query_params.get("chat_id"))
            # Update session state with this chat ID
            session_state["chat_id"] = chat_id_param
        except (ValueError, TypeError):
            logger.log_message("Invalid chat_id parameter", level=logging.WARNING)
            # Continue without updating chat_id

    # Check for user_id in query parameters
    if "user_id" in request_obj.query_params:
        try:
            user_id = int(request_obj.query_params["user_id"])
            session_state["user_id"] = user_id
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid user_id in query params. Please provide a valid integer."
            )


def _validate_agent_name(agent_name: str):
    """Validate that the requested agent(s) exist"""
    if "," in agent_name:
        agent_list = [agent.strip() for agent in agent_name.split(",")]
        for agent in agent_list:
            if agent not in AVAILABLE_AGENTS:
                available = list(AVAILABLE_AGENTS.keys())
                raise HTTPException(
                    status_code=404, 
                    detail=f"Agent '{agent}' not found. Available agents: {available}"
                )
    elif agent_name not in AVAILABLE_AGENTS:
        available = list(AVAILABLE_AGENTS.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_name}' not found. Available agents: {available}"
        )


def _prepare_query_with_context(query: str, session_state: dict) -> str:
    """Prepare the query with chat context from previous messages"""
    chat_id = session_state.get("chat_id")
    if not chat_id:
        return query
        
    # Get chat manager from app state
    chat_manager = app.state._session_manager.chat_manager
    # Get recent messages
    recent_messages = chat_manager.get_recent_chat_history(chat_id, limit=MAX_RECENT_MESSAGES)
    # Extract response history
    chat_context = chat_manager.extract_response_history(recent_messages)
    
    # Append context to the query if available
    if chat_context:
        return f"### Current Query:\n{query}\n\n{chat_context}"
    return query


def _track_model_usage(session_state: dict, enhanced_query: str, response, processing_time_ms: int):
    """Track model usage statistics in the database"""
    try:
        ai_manager = app.state.get_ai_manager()
        
        # Validate required fields for database operations
        user_id = session_state.get("user_id") if session_state else None
        chat_id = session_state.get("chat_id") if session_state else None
        
        # Skip tracking if user_id or chat_id are missing
        if not user_id:
            logger.log_message("Skipping usage tracking: user_id missing", level=logging.INFO)
            user_id = None  # Explicitly set to None for DB insertion
        
        if not chat_id:
            logger.log_message("Skipping usage tracking: chat_id missing", level=logging.INFO)
            chat_id = None  # Explicitly set to None for DB insertion
        
        # Get model configuration
        model_config = session_state.get("model_config", DEFAULT_MODEL_CONFIG)
        model_name = model_config.get("model", DEFAULT_MODEL_CONFIG["model"])
        provider = ai_manager.get_provider_for_model(model_name)
        
        # Calculate token usage
        try:
            # Try exact tokenization
            prompt_tokens = len(ai_manager.tokenizer.encode(enhanced_query))
            completion_tokens = len(ai_manager.tokenizer.encode(str(response)))
            total_tokens = prompt_tokens + completion_tokens
        except Exception as token_error:
            # Fall back to estimation
            logger.log_message(f"Tokenization error: {str(token_error)}", level=logging.WARNING)
            prompt_words = len(enhanced_query.split())
            completion_words = len(str(response).split())
            prompt_tokens = int(prompt_words * DEFAULT_TOKEN_RATIO)
            completion_tokens = int(completion_words * DEFAULT_TOKEN_RATIO)
            total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        cost = ai_manager.calculate_cost(model_name, prompt_tokens, completion_tokens)
        
        # Save usage to database (only if at least one of user_id or chat_id is provided)
        try:
            ai_manager.save_usage_to_db(
                user_id=user_id,
                chat_id=chat_id,
                model_name=model_name,
                provider=provider,
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(total_tokens),
                query_size=len(enhanced_query),
                response_size=len(str(response)),
                cost=round(cost, 7),
                request_time_ms=processing_time_ms,
                is_streaming=False
            )
        except Exception as db_error:
            logger.log_message(f"Database error when saving usage: {str(db_error)}", level=logging.ERROR)
    except Exception as e:
        # Log but don't fail the request if usage tracking fails
        logger.log_message(f"Failed to track model usage: {str(e)}", level=logging.ERROR)


async def _generate_streaming_responses(session_state: dict, query: str, session_lm):
    """Generate streaming responses for chat_with_all endpoint"""
    overall_start_time = time.time()
    total_response = ""
    total_inputs = ""
    usage_records = []

    try:
        # Add chat context from previous messages
        enhanced_query = _prepare_query_with_context(query, session_state)
        
        # Use the session model for this specific request
        with dspy.context(lm=session_lm):
            try:
                # Get the plan
                plan_response = await asyncio.wait_for(
                    asyncio.to_thread(session_state["ai_system"].get_plan, enhanced_query),
                    timeout=REQUEST_TIMEOUT_SECONDS
                )
                
                plan_description = format_response_to_markdown(
                    {"analytical_planner": plan_response}, 
                    dataframe=session_state["current_df"]
                )
                
                # Check if plan is valid
                if plan_description == RESPONSE_ERROR_INVALID_QUERY:
                    yield json.dumps({
                        "agent": "Analytical Planner",
                        "content": plan_description,
                        "status": "error"
                    }) + "\n"
                    return
                
                yield json.dumps({
                    "agent": "Analytical Planner",
                    "content": plan_description,
                    "status": "success" if plan_description else "error"
                }) + "\n"
                
                # Track planner usage
                if session_state.get("user_id"):
                    planner_tokens = _estimate_tokens(ai_manager=app.state.ai_manager, 
                                                    input_text=enhanced_query, 
                                                    output_text=plan_description)
                    
                    usage_records.append(_create_usage_record(
                        session_state=session_state,
                        model_name=session_state.get("model_config", DEFAULT_MODEL_CONFIG)["model"],
                        prompt_tokens=planner_tokens["prompt"],
                        completion_tokens=planner_tokens["completion"],
                        query_size=len(enhanced_query),
                        response_size=len(plan_description),
                        processing_time_ms=int((time.time() - overall_start_time) * 1000),
                        is_streaming=False
                    ))
                
                # Execute the plan with well-managed concurrency
                async for agent_name, inputs, response in _execute_plan_with_timeout(
                    session_state["ai_system"], enhanced_query, plan_response):
                    
                    if agent_name == "plan_not_found":
                        yield json.dumps({
                            "agent": "Analytical Planner",
                            "content": "**No plan found**\n\nPlease try again with a different query or try using a different model.",
                            "status": "error"
                        }) + "\n"
                        return
                    
                    formatted_response = format_response_to_markdown(
                        {agent_name: response}, 
                        dataframe=session_state["current_df"]
                    ) or "No response generated"

                    if formatted_response == RESPONSE_ERROR_INVALID_QUERY:
                        yield json.dumps({
                            "agent": agent_name,
                            "content": formatted_response,
                            "status": "error"
                        }) + "\n"
                        return
                        
                    # if "code_combiner_agent" in agent_name:
                    #     # logger.log_message(f"[>] Code combiner response: {response}", level=logging.INFO)
                    #     total_response += str(response) if response else ""
                    #     total_inputs += str(inputs) if inputs else ""

                    # Send response chunk
                    yield json.dumps({
                        "agent": agent_name.split("__")[0] if "__" in agent_name else agent_name,
                        "content": formatted_response,
                        "status": "success" if response else "error"
                    }) + "\n"
                    
                    # Track agent usage for future batch DB write
                    if session_state.get("user_id"):
                        agent_tokens = _estimate_tokens(
                            ai_manager=app.state.ai_manager,
                            input_text=str(inputs),
                            output_text=str(response)
                        )
                        
                        # Get appropriate model name for code combiner
                        if "code_combiner_agent" in agent_name and "__" in agent_name:
                            provider = agent_name.split("__")[1]
                            model_name = _get_model_name_for_provider(provider)
                        else:
                            model_name = session_state.get("model_config", DEFAULT_MODEL_CONFIG)["model"]

                        usage_records.append(_create_usage_record(
                            session_state=session_state,
                            model_name=model_name,
                            prompt_tokens=agent_tokens["prompt"],
                            completion_tokens=agent_tokens["completion"],
                            query_size=len(str(inputs)),
                            response_size=len(str(response)),
                            processing_time_ms=int((time.time() - overall_start_time) * 1000),
                            is_streaming=True
                        ))
                        
            except asyncio.TimeoutError:
                yield json.dumps({
                    "agent": "planner",
                    "content": "The request timed out. Please try a simpler query.",
                    "status": "error"
                }) + "\n"
                return
            except Exception as e:
                logger.log_message(f"Error in streaming response: {str(e)}", level=logging.ERROR)
                yield json.dumps({
                    "agent": "planner",
                    "content": "An error occurred while generating responses. Please try again!",
                    "status": "error"
                }) + "\n"
                
            # Batch write usage records to DB
            if usage_records and session_state.get("user_id"):
                try:
                    # In a real implementation, you would batch these writes
                    # For now, we're writing them one by one but could be optimized
                    ai_manager = app.state.get_ai_manager()
                    for record in usage_records:
                        ai_manager.save_usage_to_db(**record)
                except Exception as db_error:
                    logger.log_message(f"Failed to save usage records: {str(db_error)}", level=logging.ERROR)
           
    except Exception as e:
        logger.log_message(f"Streaming response generation failed: {str(e)}", level=logging.ERROR)
        yield json.dumps({
            "agent": "planner",
            "content": "An error occurred while generating responses. Please try again!",
            "status": "error"
        }) + "\n"


def _estimate_tokens(ai_manager, input_text: str, output_text: str) -> dict:
    """Estimate token counts, with fallback for tokenization errors"""
    try:
        # Try exact tokenization
        prompt_tokens = len(ai_manager.tokenizer.encode(input_text))
        completion_tokens = len(ai_manager.tokenizer.encode(output_text))
    except Exception:
        # Fall back to estimation
        prompt_words = len(input_text.split())
        completion_words = len(output_text.split())
        prompt_tokens = int(prompt_words * DEFAULT_TOKEN_RATIO)
        completion_tokens = int(completion_words * DEFAULT_TOKEN_RATIO)
    
    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": prompt_tokens + completion_tokens
    }


def _create_usage_record(session_state: dict, model_name: str, prompt_tokens: int, 
                        completion_tokens: int, query_size: int, response_size: int,
                        processing_time_ms: int, is_streaming: bool) -> dict:
    """Create a usage record for the database"""
    ai_manager = app.state.get_ai_manager()
    provider = ai_manager.get_provider_for_model(model_name)
    cost = ai_manager.calculate_cost(model_name, prompt_tokens, completion_tokens)
    
    return {
        "user_id": session_state.get("user_id"),
        "chat_id": session_state.get("chat_id"),
        "model_name": model_name,
        "provider": provider,
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "total_tokens": int(prompt_tokens + completion_tokens),
        "query_size": query_size,
        "response_size": response_size,
        "cost": round(cost, 7),
        "request_time_ms": processing_time_ms,
        "is_streaming": is_streaming
    }


def _get_model_name_for_provider(provider: str) -> str:
    """Get the model name for a provider"""
    provider_model_map = {
        "openai": "o3-mini",
        "anthropic": "claude-3-7-sonnet-latest",
        "gemini": "gemini-2.5-pro-preview-03-25"
    }
    return provider_model_map.get(provider, "o3-mini")


async def _execute_plan_with_timeout(ai_system, enhanced_query, plan_response):
    """Execute the plan with timeout handling for each step"""
    try:
        # Use asyncio.create_task to run the execute_plan coroutine
        async for agent_name, inputs, response in ai_system.execute_plan(enhanced_query, plan_response):
            # Yield results as they come
            yield agent_name, inputs, response
    except Exception as e:
        logger.log_message(f"Error executing plan: {str(e)}", level=logging.ERROR)
        yield "error", None, {"error": "An error occurred during plan execution"}


# Add an endpoint to list available agents
@app.get("/agents", response_model=dict)
async def list_agents():
    return {
        "available_agents": list(AVAILABLE_AGENTS.keys()),
        "description": "List of available specialized agents that can be called using @agent_name"
    }

@app.get("/health", response_model=dict)
async def health():
    return {"message": "API is healthy and running"}

@app.get("/")
async def index():
    return {
        "title": "Welcome to the AI Analytics API",
        "message": "Explore our API for advanced analytics and visualization tools designed to empower your data-driven decisions.",
        "description": "Utilize our powerful agents and models to gain insights from your data effortlessly.",
        "colors": {
            "primary": "#007bff",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545",
        },
        "features": [
            "Real-time data processing",
            "Customizable visualizations",
            "Seamless integration with various data sources",
            "User-friendly interface for easy navigation",
            "Custom Analytics",
        ],
    }

@app.post("/chat_history_name")
async def chat_history_name(request: dict, session_id: str = Depends(get_session_id_dependency)):
    query = request.get("query")
    name = None
    
    lm = dspy.LM(model="gpt-4o-mini", max_tokens=300, temperature=0.5)
    
    with dspy.context(lm=lm):
        name = app.state.get_chat_history_name_agent()(query=str(query))
        
    return {"name": name.name if name else "New Chat"}

# In the section where routers are included, add the session_router
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(code_router)
app.include_router(session_router)
app.include_router(automotive_router)

# Add these new routes for file server integration
class DataAnalysisRequest(BaseModel):
    query: str
    filename: Optional[str] = None

@app.get("/api/file-server/datasets", response_model=dict)
async def get_available_datasets():
    """Get a list of available datasets from the file server"""
    try:
        response = requests.get(f"{FILE_SERVER_URL}/files")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch datasets: {response.status_code}", "files": []}
    except Exception as e:
        logger.log_message(f"Error fetching datasets from file server: {str(e)}", level=logging.ERROR)
        return {"error": f"Exception: {str(e)}", "files": []}

@app.get("/api/file-server/health", response_model=dict)
async def check_file_server_health():
    """Check if the file server is running"""
    try:
        response = requests.get(f"{FILE_SERVER_URL}/health")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"File server returned status code {response.status_code}"}
    except Exception as e:
        logger.log_message(f"Error connecting to file server: {str(e)}", level=logging.ERROR)
        return {"status": "error", "message": f"Connection error: {str(e)}"}

@app.get("/api/file-server/default-dataset", response_model=dict)
async def get_default_dataset():
    """Get the default dataset from the file server"""
    try:
        response = requests.get(f"{FILE_SERVER_URL}/api/default-dataset")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch default dataset: {response.status_code}"}
    except Exception as e:
        logger.log_message(f"Error fetching default dataset from file server: {str(e)}", level=logging.ERROR)
        return {"error": f"Exception: {str(e)}"}

def load_dataset_from_file_server(filename):
    """Load a dataset from the file server"""
    # Check if dataset is already in cache
    if filename in datasets_cache:
        return datasets_cache[filename], None
    
    try:
        # Try to get the file from the exports directory
        response = requests.get(f"{FILE_SERVER_URL}/exports/{filename}")
        
        if response.status_code == 200:
            # Parse CSV data
            csv_data = response.text
            df = pd.read_csv(StringIO(csv_data))
            
            # Cache the dataframe for future use
            datasets_cache[filename] = df
            
            return df, None
        else:
            return None, f"Failed to load dataset {filename}: {response.status_code}"
    except Exception as e:
        return None, f"Exception loading dataset {filename}: {str(e)}"

def create_analysis_prompt(query, dataframe):
    """Generate analysis prompt for the AI model based on the query and dataframe"""
    # Get dataframe info
    num_rows, num_cols = dataframe.shape
    columns = dataframe.columns.tolist()
    data_sample = dataframe.head(5).to_csv(index=False)
    
    # Create enhanced prompt with data context
    enhanced_prompt = f"""Analyze the following dataset based on this query: {query}

Dataset Information:
- Number of rows: {num_rows}
- Number of columns: {num_cols}
- Columns: {', '.join(columns)}

Here's a sample of the data:
{data_sample}

Please provide a detailed analysis addressing the query. Include relevant statistics, trends, and insights. If appropriate, suggest visualizations that would help understand the data better.
"""
    return enhanced_prompt

@app.post("/api/analyze-file")
async def analyze_file(
    request: DataAnalysisRequest,
    request_obj: Request,
    session_id: str = Depends(get_session_id_dependency)
):
    """Analyze a dataset from the file server"""
    session_state = app.state.get_session_state(session_id)
    
    try:
        # Get the query and filename
        query = request.query
        filename = request.filename
        
        # If no filename provided, check available datasets and use the first one
        if not filename:
            datasets_response = await get_available_datasets()
            if "error" in datasets_response:
                return {"error": datasets_response["error"], "success": False}
            
            if "files" in datasets_response and datasets_response["files"]:
                filename = datasets_response["files"][0]
            else:
                return {"error": "No datasets available", "success": False}
        
        # Load the dataset
        df, error = load_dataset_from_file_server(filename)
        if error:
            return {"error": error, "success": False}
        
        # Create enhanced prompt for analysis
        enhanced_prompt = create_analysis_prompt(query, df)
        
        # Get session-specific model for this request
        session_lm = get_session_lm(session_state)
        
        # Record start time for timing
        start_time = time.time()
        
        # Execute the query
        with dspy.context(lm=session_lm):
            response = await asyncio.wait_for(
                asyncio.to_thread(lambda: query_gemini(enhanced_prompt, session_lm)),
                timeout=REQUEST_TIMEOUT_SECONDS
            )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Only track usage if user_id and chat_id are present
        if session_state and "user_id" in session_state and "chat_id" in session_state:
            try:
                # Add tracking and usage data
                _track_model_usage(session_state, enhanced_prompt, response, processing_time_ms)
            except Exception as usage_error:
                # Log but don't fail the entire request
                logger.log_message(f"Error tracking usage: {str(usage_error)}", level=logging.ERROR)
        
        # Add dataset name to response
        response_data = {
            "response": response,
            "dataset": filename,
            "success": True,
            "processing_time_ms": processing_time_ms
        }
        
        return response_data
    
    except asyncio.TimeoutError:
        logger.log_message(f"Analysis request timed out for {filename}", level=logging.WARNING)
        return {"error": "Request timed out. Please try a simpler query.", "success": False}
    except Exception as e:
        logger.log_message(f"Error in analyze_file: {str(e)}", level=logging.ERROR)
        return {"error": f"Error: {str(e)}", "success": False}

def query_gemini(prompt, session_lm):
    """Execute a query using Gemini"""
    try:
        # Extract model name and normalize it for Gemini
        model = session_lm.model if hasattr(session_lm, 'model') else "gemini-1.5-pro"
        if model.startswith("gemini/"):
            model = model.replace("gemini/", "")
            
        # Get the API key (with fallback to environment variable)
        api_key = None
        if hasattr(session_lm, 'api_key') and session_lm.api_key:
            api_key = session_lm.api_key
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            
        if not api_key:
            logger.log_message("No API key found for Gemini", level=logging.ERROR)
            return "Error: No API key configured for Gemini. Please check your settings."
            
        # Get temperature and max tokens with fallbacks
        temperature = getattr(session_lm, 'temperature', 0.7)
        max_tokens = getattr(session_lm, 'max_tokens', 4000)
        
        # Create the API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Extract the generated text
            if "candidates" in result and len(result["candidates"]) > 0:
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                return generated_text
            else:
                return f"No candidates in response: {str(result)}"
        else:
            return f"API error: {response.status_code} - {response.text}"
    except Exception as e:
        logger.log_message(f"Error in query_gemini: {str(e)}", level=logging.ERROR)
        return f"Error: {str(e)}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)