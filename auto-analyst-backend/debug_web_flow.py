#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import dspy
import asyncio
from dotenv import load_dotenv
from app import get_session_lm, AVAILABLE_AGENTS, app
from src.agents.agents import auto_analyst_ind
from scripts.format_response import format_response_to_markdown

load_dotenv()

async def debug_web_flow():
    """Debug the exact web API flow to find where the auth error occurs"""
    
    print("--- Simulating exact web API flow ---")
    
    # Step 1: Get session state (like the web API does)
    session_id = "debug-web-flow"
    session_state = app.state.get_session_state(session_id)
    
    print(f"Session state model config: {session_state['model_config']}")
    print(f"Has current_df: {session_state['current_df'] is not None}")
    print(f"Dataset shape: {session_state['current_df'].shape if session_state['current_df'] is not None else 'None'}")
    
    # Step 2: Prepare query (like the web API does)
    query = "How many vehicles do we have in total?"
    enhanced_query = query  # Simplified for debugging
    
    # Step 3: Initialize agent (like the web API does)
    agent_name = "data_viz_agent"
    agent = auto_analyst_ind(agents=[AVAILABLE_AGENTS[agent_name]], retrievers=session_state["retrievers"])
    
    # Step 4: Get session LM (like the web API does)
    session_lm = get_session_lm(session_state)
    print(f"Session LM model: {getattr(session_lm, 'model', 'UNKNOWN')}")
    
    # Step 5: Execute agent with context (like the web API does)
    print("\n--- Executing agent with dspy context ---")
    try:
        with dspy.context(lm=session_lm):
            response = await asyncio.wait_for(
                asyncio.to_thread(agent, enhanced_query, agent_name),
                timeout=60
            )
        print(f"Agent response type: {type(response)}")
        print(f"Agent response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        
        # Step 6: Format response (like the web API does)
        print("\n--- Formatting response ---")
        formatted_response = format_response_to_markdown(response, agent_name, session_state["current_df"])
        print(f"Formatted response: {formatted_response[:200]}...")
        
        if "Authentication failed" in formatted_response:
            print("\n🔑 AUTHENTICATION ERROR FOUND IN FORMATTED RESPONSE!")
            print("Raw agent response:")
            print(response)
        else:
            print("\n✅ No authentication error found!")
            
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_web_flow()) 