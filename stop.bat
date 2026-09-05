@echo off
echo Stopping API Consumer Console services on ports 8080, 8100, 8101, 8200...

for %%P in (8080 8100 8101 8200) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING"') do (
        echo Killing process PID %%a on port %%P...
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo All services on ports 8080, 8100, 8101, 8200 stopped.
