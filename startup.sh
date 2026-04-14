#!/bin/bash
set -e
cd /home/site/wwwroot
pip install --quiet -r requirements.txt
exec uvicorn src.app:app --host 0.0.0.0 --port 8000
