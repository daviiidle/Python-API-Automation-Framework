@echo off
setlocal

echo ===========================================
echo  Banking API Test Framework - Wiremock Control
echo ===========================================

REM Default port if not set
if not defined PORT set PORT=8081

echo Stopping any existing WireMock processes...

REM Kill any existing WireMock processes
tasklist | find "java.exe" | find "wiremock" >nul 2>&1
if not errorlevel 1 (
    echo Found running WireMock processes, terminating...
    taskkill /f /im java.exe /fi "WINDOWTITLE eq *wiremock*" >nul 2>&1
    taskkill /f /im java.exe /fi "COMMANDLINE eq *wiremock-standalone.jar*" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Also kill by port if needed
for /f "tokens=5" %%a in ('netstat -aon ^| find ":%PORT%" ^| find "LISTENING"') do (
    echo Killing process using port %PORT% (PID: %%a)
    taskkill /f /pid %%a >nul 2>&1
)

echo Starting fresh WireMock instance on port %PORT%...

REM Check if wiremock-standalone.jar exists in the test framework
if exist "wiremock-standalone.jar" (
    echo Using WireMock JAR from test framework directory
    start "WireMock Server" /min java -jar wiremock-standalone.jar ^
        --port %PORT% ^
        --global-response-templating ^
        --verbose
) else if exist "C:\Users\D\Wiremock\wiremock-standalone.jar" (
    echo Using WireMock JAR from C:\Users\D\Wiremock\
    cd /d "C:\Users\D\Wiremock"
    start "WireMock Server" /min java -jar wiremock-standalone.jar ^
        --port %PORT% ^
        --global-response-templating ^
        --verbose
) else (
    echo Error: wiremock-standalone.jar not found!
    echo Please ensure WireMock JAR is available in:
    echo   1. Current directory, or
    echo   2. C:\Users\D\Wiremock\
    exit /b 1
)

echo Waiting for WireMock to start...
timeout /t 5 /nobreak >nul

REM Verify WireMock is running
curl -s http://localhost:%PORT%/__admin/health >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not verify WireMock startup
) else (
    echo ✅ WireMock is running successfully on port %PORT%
)

echo Ready for test execution!
endlocal