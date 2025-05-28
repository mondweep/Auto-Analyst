#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
from src.agents.agents import data_viz_agent, auto_analyst_ind
from src.agents.retrievers.retrievers import *
import dspy
from dotenv import load_dotenv

load_dotenv()

def test_agent_directly():
    """Test what the agent actually returns"""
    
    # Load the CSV data
    try:
        df = pd.read_csv("exports/vehicles.csv")
        print(f"Loaded CSV with {len(df)} vehicles")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Create a simple LM for testing
    try:
        lm = dspy.LM(
            model="gemini/gemini-1.5-pro",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            max_tokens=4000
        )
        
        # Set up the agent
        with dspy.context(lm=lm):
            # Create simple retrievers
            from llama_index.core import Document, VectorStoreIndex
            
            # Create minimal styling instructions
            styling_docs = [Document(text="Use plotly for visualizations")]
            style_index = VectorStoreIndex.from_documents(styling_docs)
            
            # Create data description
            data_desc = f"Dataset with {len(df)} vehicles. Columns: {', '.join(df.columns)}"
            data_docs = [Document(text=data_desc)]
            data_index = VectorStoreIndex.from_documents(data_docs)
            
            retrievers = {"style_index": style_index, "dataframe_index": data_index}
            
            # Test the agent directly
            agent = auto_analyst_ind(agents=[data_viz_agent], retrievers=retrievers)
            
            print("\n--- Testing agent with simple query ---")
            query = "How many vehicles do we have in total?"
            
            try:
                response = agent(query, "data_viz_agent")
                print(f"Agent response type: {type(response)}")
                print(f"Agent response: {response}")
                
                # Try to understand the structure
                if hasattr(response, '__dict__'):
                    print(f"Response attributes: {response.__dict__}")
                
                return response
                
            except Exception as e:
                print(f"Agent execution error: {e}")
                import traceback
                traceback.print_exc()
                return None
                
    except Exception as e:
        print(f"Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_directly() 