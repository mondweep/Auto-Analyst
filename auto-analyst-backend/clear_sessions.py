#!/usr/bin/env python3

"""
Clear all session states to force fresh sessions with updated API keys
"""

import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.managers.session_manager import SessionManager

def clear_all_sessions():
    """Clear all existing sessions to force fresh start with new API keys"""
    
    # Create a dummy session manager
    dummy_styling = ["dummy"]
    dummy_agents = {}
    
    try:
        session_manager = SessionManager(dummy_styling, dummy_agents)
        
        # Clear all sessions
        session_count = len(session_manager._sessions)
        session_manager._sessions.clear()
        
        print(f"✅ Cleared {session_count} existing sessions")
        print("🔄 All new sessions will use updated API keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing sessions: {e}")
        return False

if __name__ == "__main__":
    success = clear_all_sessions()
    if success:
        print("\n🎉 Session clearing completed successfully!")
        print("💡 The backend will now create fresh sessions with your new API key.")
    else:
        print("\n❌ Session clearing failed. You may need to restart the backend server.") 