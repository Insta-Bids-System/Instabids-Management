#!/usr/bin/env python3
"""
Server startup script that ensures correct Supabase configuration
"""
import os
import sys
import uvicorn

def setup_environment():
    """Set correct environment variables"""
    # Force correct Supabase configuration
    os.environ['SUPABASE_URL'] = 'https://lmbpvkfcfhdfaihigfdu.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjgzNTIsImV4cCI6MjA3MzcwNDM1Mn0.WH4-iA_FnW1EqGTl-hcpotzqBGgeCutKWBBMaa6Tnmg'
    os.environ['SUPABASE_SERVICE_KEY'] = ''
    
    # Clear any cached modules
    modules_to_clear = []
    for module_name in sys.modules:
        if any(x in module_name for x in ['config', 'supabase', 'services']):
            modules_to_clear.append(module_name)
    
    for module_name in modules_to_clear:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    print("Environment setup complete:")
    print(f"SUPABASE_URL: {os.environ['SUPABASE_URL']}")
    print(f"SUPABASE_ANON_KEY: {os.environ['SUPABASE_ANON_KEY'][:20]}...")

def main():
    """Start the server with correct configuration"""
    print("=== InstaBids API Server Startup ===")
    
    # Setup environment
    setup_environment()
    
    # Test Supabase connection before starting server
    try:
        from supabase import create_client
        client = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_ANON_KEY']
        )
        print("SUCCESS: Supabase connection test passed")
    except Exception as e:
        print(f"FAILED: Supabase connection test - {e}")
        return
    
    # Start server
    print("Starting FastAPI server on port 8000...")
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()