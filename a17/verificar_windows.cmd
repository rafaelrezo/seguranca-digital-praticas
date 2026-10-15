@echo off
route print 10.8.0.1
curl.exe --noproxy "*" --max-time 5 http://10.8.0.1:8080/
exit /b %errorlevel%
