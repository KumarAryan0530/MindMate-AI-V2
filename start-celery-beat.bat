@echo off
cd /d E:\all-projects\SafeMind-AI
echo Starting Celery Beat for SafeMind-AI...
echo.
echo This will check for scheduled calls every minute.
echo Keep this window open while using voice calls.
echo.
E:\all-projects\SafeMind-AI\venv\Scripts\celery.exe -A perplex beat -l info
pause
