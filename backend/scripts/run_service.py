#!/usr/bin/env python3
"""Script to run individual services for development."""

import subprocess
import sys
import argparse
import os
from pathlib import Path


def run_entry_ingestor():
    """Run the entry ingestor service."""
    print("🚀 Starting Entry Ingestor Service...")
    
    # Set PYTHONPATH to include the backend directory
    backend_dir = Path(__file__).parent.parent
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    cmd = [
        "python", "-m", "uvicorn",
        "services.entry_ingestor.app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    subprocess.run(cmd, env=env, cwd=backend_dir)


def run_nlp_agent():
    """Run the NLP agent service."""
    print("🚀 Starting NLP Agent Service...")
    
    # Set PYTHONPATH to include the backend directory
    backend_dir = Path(__file__).parent.parent
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    cmd = [
        "python", "-m", "uvicorn",
        "services.nlp_agent.app.main:app",
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--reload"
    ]
    
    subprocess.run(cmd, env=env, cwd=backend_dir)


def main():
    parser = argparse.ArgumentParser(description="Run Aura Journal backend services")
    parser.add_argument(
        "service",
        choices=["entry-ingestor", "nlp-agent"],
        help="Service to run"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run on (overrides default)"
    )
    
    args = parser.parse_args()
    
    if args.service == "entry-ingestor":
        run_entry_ingestor()
    elif args.service == "nlp-agent":
        run_nlp_agent()


if __name__ == "__main__":
    main()
