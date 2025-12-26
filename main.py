#!/usr/bin/env python3
"""
Main entry point for Replit deployment
"""
import subprocess
import sys

if __name__ == "__main__":
    # Run the FastAPI server
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "simple_api:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

