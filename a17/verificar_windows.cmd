@echo off
route print
curl.exe --noproxy "*" --max-time 5 http://10.77.2.10:8080/
exit /b %errorlevel%
