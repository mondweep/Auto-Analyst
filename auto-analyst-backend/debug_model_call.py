#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

import dspy
from dotenv import load_dotenv
from app import get_session_lm

load_dotenv()

def debug_model_call():
    """Debug the actual model call being made"""
    
    print("Environment variables:")
    print(f"MODEL_PROVIDER: {os.getenv('MODEL_PROVIDER')}")
    print(f"MODEL_NAME: {os.getenv('MODEL_NAME')}")
    print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20]}...")
    
    # Create a mock session state
    session_state = {
        "model_config": {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "temperature": 0.7,
            "max_tokens": 4000
        }
    }
    
    print(f"\nSession model config: {session_state['model_config']}")
    
    # Get the session LM
    session_lm = get_session_lm(session_state)
    
    print(f"\nSession LM details:")
    print(f"Type: {type(session_lm)}")
    print(f"Model: {getattr(session_lm, 'model', 'UNKNOWN')}")
    print(f"API Key: {getattr(session_lm, 'api_key', 'UNKNOWN')[:20]}...")
    print(f"Temperature: {getattr(session_lm, 'temperature', 'UNKNOWN')}")
    print(f"Max tokens: {getattr(session_lm, 'max_tokens', 'UNKNOWN')}")
    
    # Try to use the LM directly
    print(f"\n--- Testing direct LM call ---")
    try:
        with dspy.context(lm=session_lm):
            response = session_lm("Hello, this is a test")
            print(f"Success: {response}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        
    # Try using dspy.LM directly with the same configuration
    print(f"\n--- Testing direct dspy.LM call ---")
    try:
        direct_lm = dspy.LM(
            model="gemini/gemini-1.5-pro",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            max_tokens=4000
        )
        
        print(f"Direct LM model: {direct_lm.model}")
        print(f"Direct LM API key: {direct_lm.api_key[:20]}...")
        
        response = direct_lm("Hello, this is a direct test")
        print(f"Direct Success: {response}")
    except Exception as e:
        print(f"Direct Error: {e}")
        print(f"Direct Error type: {type(e)}")

if __name__ == "__main__":
    debug_model_call() 