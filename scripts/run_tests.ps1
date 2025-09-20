# Banking API BDD Test Framework - PowerShell Runner
# Ensures 100% pass rate by restarting Wiremock before each test run

param(
    [string]$Tags = "",
    [string]$Format = "pretty",
    [switch]$SkipWiremock = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Banking API BDD Test Framework - PowerShell Runner" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\run_tests.ps1                    # Run all tests with fresh Wiremock"
    Write-Host "  .\run_tests.ps1 -Tags @smoke       # Run smoke tests only"
    Write-Host "  .\run_tests.ps1 -Tags @accounts    # Run account tests only"
    Write-Host "  .\run_tests.ps1 -SkipWiremock      # Skip Wiremock restart"
    Write-Host "  .\run_tests.ps1 -Help              # Show this help"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Tags       Behave tags to run (e.g., @smoke, @accounts, @regression)"
    Write-Host "  -Format     Output format (default: pretty)"
    Write-Host "  -SkipWiremock  Skip Wiremock restart (faster, but may have failures)"
    Write-Host ""
    exit 0
}

Write-Host "🏦 Banking API BDD Test Framework" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV -and -not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "⚠️  Virtual environment not found!" -ForegroundColor Yellow
    Write-Host "Please run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment if not already activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Build command
$cmd = @("python", "scripts\run_tests_with_wiremock.py", "--format", $Format)

if ($Tags) {
    $cmd += "--tags"
    $cmd += $Tags
    Write-Host "🎯 Running tests with tags: $Tags" -ForegroundColor Green
} else {
    Write-Host "🧪 Running all tests" -ForegroundColor Green
}

if ($SkipWiremock) {
    $cmd += "--skip-wiremock"
    Write-Host "⚠️  Skipping Wiremock restart (may cause test failures)" -ForegroundColor Yellow
} else {
    Write-Host "🔄 Will restart Wiremock for 100% pass rate" -ForegroundColor Green
}

Write-Host "📝 Format: $Format" -ForegroundColor Gray
Write-Host ""

# Execute the command
try {
    & $cmd[0] $cmd[1..($cmd.Length-1)]
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ Tests completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Tests failed with exit code: $exitCode" -ForegroundColor Red
    }
    
    exit $exitCode
} catch {
    Write-Host ""
    Write-Host "❌ Error executing tests: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}