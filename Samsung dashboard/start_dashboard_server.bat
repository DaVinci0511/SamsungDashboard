@echo off
title Samsung Dashboard Server
cd /d "%~dp0"
echo ===================================================
echo     Samsung Shipment Dashboard - Web Server
echo ===================================================
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP: =%

echo Local PC Access:       http://localhost:8080
echo Same Network/Boss:     http://%IP%:8080
echo.
echo Press Ctrl+C or close this window to stop the server.
echo ===================================================
echo.
py -m http.server 8080
pause

