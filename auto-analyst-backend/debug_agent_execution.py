#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import dspy
from dotenv import load_dotenv
from app import get_session_lm, AVAILABLE_AGENTS
from src.agents.agents import auto_analyst_ind
from src.agents.retrievers.retrievers import make_data
from llama_index.core import Document, VectorStoreIndex

load_dotenv()

def debug_agent_execution():
    """Debug the agent execution to find where the auth error comes from"""
    
    print("--- Setting up test environment ---")
    
    # Load some test data
    df = pd.read_csv("exports/vehicles.csv")
    print(f"Loaded {len(df)} vehicles")
    
    # Create basic retrievers
    styling_docs = [Document(text="Use plotly for visualizations")]
    style_index = VectorStoreIndex.from_documents(styling_docs)
    
    data_desc = f"Dataset with {len(df)} vehicles. Columns: {', '.join(df.columns)}"
    data_docs = [Document(text=data_desc)]
    data_index = VectorStoreIndex.from_documents(data_docs)
    
    retrievers = {"style_index": style_index, "dataframe_index": data_index}
    
    # Create session state with proper model config
    session_state = {
        "model_config": {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "temperature": 0.7,
            "max_tokens": 4000
        },
        "current_df": df,
        "retrievers": retrievers
    }
    
    print(f"Session config: {session_state['model_config']}")
    
    # Get session LM
    session_lm = get_session_lm(session_state)
    
    # Test the simple LM call first
    print("\n--- Testing simple LM call ---")
    try:
        with dspy.context(lm=session_lm):
            response = session_lm("Hello")
            print(f"LM call success: {response}")
    except Exception as e:
        print(f"LM call error: {e}")
        return
    
    # Test agent execution
    print("\n--- Testing agent execution ---")
    try:
        # Initialize agent
        agent = auto_analyst_ind(agents=[AVAILABLE_AGENTS["data_viz_agent"]], retrievers=retrievers)
        
        # Execute with session LM context
        with dspy.context(lm=session_lm):
            query = "How many vehicles do we have in total?"
            print(f"Testing query: {query}")
            
            response = agent(query, "data_viz_agent")
            print(f"Agent response type: {type(response)}")
            print(f"Agent response: {response}")
            
    except Exception as e:
        print(f"Agent execution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_agent_execution() 