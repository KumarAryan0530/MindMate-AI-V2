@echo off
cd /d E:\all-projects\SafeMind-AI
echo Starting Daphne Server for SafeMind-AI Voice Calls...
echo.
echo This will start the ASGI server with WebSocket support.
echo Keep this window open while using voice calls.
echo.
E:\all-projects\SafeMind-AI\venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 perplex.asgi:application
pause
