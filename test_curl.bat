@echo off
echo Testing enhance-prompt endpoint...
echo.

curl -X POST "http://127.0.0.1:8000/enhance-prompt" ^
-H "Content-Type: application/json" ^
-d "{\"prompt\":\"a beautiful sunset\",\"style\":\"cinematic\",\"detail_level\":\"medium\"}"

echo.
echo If you see a 500 error, restart the server with: python app.py
pause
