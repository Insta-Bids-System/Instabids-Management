#!/usr/bin/env python3
"""
Start FastAPI server with correct Supabase configuration
This script ensures the system environment variables don't interfere
"""
import os
import subprocess
import sys


def main():
    print("=== Starting InstaBids API with Correct Configuration ===")

    # Force correct environment variables
    os.environ["SUPABASE_URL"] = "https://lmbpvkfcfhdfaihigfdu.supabase.co"
    os.environ["SUPABASE_ANON_KEY"] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMjgzNTIsImV4cCI6MjA3MzcwNDM1Mn0.WH4-iA_FnW1EqGTl-hcpotzqBGgeCutKWBBMaa6Tnmg"
    )
    os.environ["SUPABASE_SERVICE_KEY"] = ""

    print(f"Environment set:")
    print(f"  SUPABASE_URL: {os.environ['SUPABASE_URL']}")
    print(f"  SUPABASE_ANON_KEY: {os.environ['SUPABASE_ANON_KEY'][:20]}...")

    # Test Supabase connection
    try:
        from supabase import create_client

        client = create_client(
            os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"]
        )
        print("SUCCESS: Supabase connection test passed")
    except Exception as e:
        print(f"FAILED: Supabase connection test - {e}")
        return

    # Start uvicorn server
    print("Starting FastAPI server...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    main()
