#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import dspy
import asyncio
from dotenv import load_dotenv
from app import get_session_lm, AVAILABLE_AGENTS, app, get_vehicles_direct
from src.agents.agents import auto_analyst_ind
from scripts.format_response import format_response_to_markdown

load_dotenv()

async def debug_vehicles_loading():
    """Debug the vehicles dataset auto-loading process"""
    
    print("--- Testing vehicles dataset auto-loading ---")
    
    # Step 1: Create a fresh session with no dataset
    session_id = "debug-vehicles-loading"
    app.state.clear_session_state(session_id)  # Clear any existing state
    session_state = app.state.get_session_state(session_id)
    
    # Step 2: Force the dataset to be None to trigger auto-loading
    session_state["current_df"] = None
    print(f"Session state current_df: {session_state['current_df']}")
    
    # Step 3: Test the vehicles loading process (like the web API does)
    try:
        print("\n--- Loading automotive data ---")
        vehicles_response = await get_vehicles_direct()
        print(f"Vehicles response type: {type(vehicles_response)}")
        print(f"Vehicles count: {len(vehicles_response) if vehicles_response else 0}")
        
        if vehicles_response and len(vehicles_response) > 0:
            # Convert to DataFrame (like the web API does)
            df = pd.DataFrame(vehicles_response)
            print(f"DataFrame shape: {df.shape}")
            print(f"DataFrame columns: {df.columns.tolist()}")
            
            # Update session with automotive dataset (like the web API does)
            print("\n--- Updating session dataset ---")
            app.state.update_session_dataset(
                session_id, 
                df, 
                "Automotive Inventory", 
                "Vehicle inventory data for analysis"
            )
            
            # Refresh session state (like the web API does)
            session_state = app.state.get_session_state(session_id)
            print(f"Updated session state model config: {session_state['model_config']}")
            print(f"Updated dataset shape: {session_state['current_df'].shape}")
            
            # Step 4: Now test agent execution with the vehicles dataset
            print("\n--- Testing agent execution with vehicles dataset ---")
            query = "How many vehicles do we have in total?"
            agent_name = "data_viz_agent"
            agent = auto_analyst_ind(agents=[AVAILABLE_AGENTS[agent_name]], retrievers=session_state["retrievers"])
            
            session_lm = get_session_lm(session_state)
            print(f"Session LM model: {getattr(session_lm, 'model', 'UNKNOWN')}")
            
            with dspy.context(lm=session_lm):
                response = await asyncio.wait_for(
                    asyncio.to_thread(agent, query, agent_name),
                    timeout=60
                )
            
            print(f"Agent response type: {type(response)}")
            
            # Format response
            formatted_response = format_response_to_markdown(response, agent_name, session_state["current_df"])
            
            if "Authentication failed" in formatted_response:
                print("\n🔑 AUTHENTICATION ERROR FOUND!")
                print("Raw agent response:")
                print(response)
            else:
                print("\n✅ No authentication error found!")
                print(f"Response preview: {formatted_response[:200]}...")
        else:
            print("❌ No vehicles data available")
            
    except Exception as e:
        print(f"Error during vehicles loading: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_vehicles_loading()) 