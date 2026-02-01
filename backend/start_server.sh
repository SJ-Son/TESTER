#!/bin/bash

# Set PYTHONPATH to include the parent directory
export PYTHONPATH="/Users/sonseongjun/TESTER:$PYTHONPATH"

# Run uvicorn
cd /Users/sonseongjun/TESTER/backend
python3 -m uvicorn src.main:app --reload --port 8000
