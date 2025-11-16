@echo off
REM start_all.bat - starts product-service and gateway in new command windows and logs output to ..\logs\

SET SCRIPT_DIR=%~dp0
SET ROOT_DIR=%SCRIPT_DIR%..\
SET LOG_DIR=%ROOT_DIR%logs

IF NOT EXIST "%LOG_DIR%" (
  mkdir "%LOG_DIR%"
)

echo Starting product-service (logs -> %LOG_DIR%\product.log)
start "product-service" cmd /c "cd /d "%ROOT_DIR%product-service" && go run main.go > "%LOG_DIR%\product.log" 2>&1"

timeout /t 1 >nul

echo Starting gateway (logs -> %LOG_DIR%\gateway.log)
start "gateway" cmd /c "cd /d "%ROOT_DIR%gateway" && go run main.go > "%LOG_DIR%\gateway.log" 2>&1"

echo Services started. Check logs in %LOG_DIR%\
echo To stop the services, close the command windows or use Task Manager to end the go.exe processes.
pause