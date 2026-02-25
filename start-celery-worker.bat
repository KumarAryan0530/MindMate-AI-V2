@echo off
cd /d E:\all-projects\SafeMind-AI
echo Starting Celery Worker for SafeMind-AI...
echo.
echo This will process scheduled voice calls and background tasks.
echo Keep this window open while using voice calls.
echo.
E:\all-projects\SafeMind-AI\venv\Scripts\celery.exe -A perplex worker -l info -P solo
pause
