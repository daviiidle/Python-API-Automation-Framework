#!/bin/bash

# Banking API BDD Test Runner Script
# Usage: ./scripts/run_tests.sh [environment] [tags] [format]

set -e

# Default values
ENVIRONMENT=${1:-test}
TAGS=${2:-@smoke}
FORMAT=${3:-pretty}
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

echo "🏦 Banking API BDD Test Framework"
echo "=================================="
echo "Environment: $ENVIRONMENT"
echo "Tags: $TAGS"
echo "Format: $FORMAT"
echo "Timestamp: $TIMESTAMP"
echo ""

# Load environment configuration
ENV_FILE="environments/.env.$ENVIRONMENT"
if [ -f "$ENV_FILE" ]; then
    echo "📁 Loading environment from: $ENV_FILE"
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "⚠️  Environment file not found: $ENV_FILE"
    echo "Using default configuration..."
fi

# Create reports directory
mkdir -p reports/allure-results reports/junit logs

# Set log file
LOG_FILE="logs/test_run_${ENVIRONMENT}_${TIMESTAMP}.log"

# Function to run tests with different formats
run_tests() {
    local test_format=$1
    local output_dir=$2
    
    echo "🧪 Running tests with format: $test_format"
    
    case $test_format in
        "allure")
            poetry run behave \
                --tags="$TAGS" \
                --format=allure_behave.formatter:AllureFormatter \
                --outdir=reports/allure-results \
                2>&1 | tee "$LOG_FILE"
            ;;
        "junit")
            poetry run behave \
                --tags="$TAGS" \
                --junit \
                --junit-directory=reports/junit \
                --format=pretty \
                2>&1 | tee "$LOG_FILE"
            ;;
        "html")
            poetry run behave \
                --tags="$TAGS" \
                --format=pretty \
                --outfile="reports/test_report_${TIMESTAMP}.txt" \
                2>&1 | tee "$LOG_FILE"
            ;;
        "pretty")
            poetry run behave \
                --tags="$TAGS" \
                --format=pretty \
                2>&1 | tee "$LOG_FILE"
            ;;
        "json")
            poetry run behave \
                --tags="$TAGS" \
                --format=json.pretty \
                --outfile="reports/test_results_${TIMESTAMP}.json" \
                2>&1 | tee "$LOG_FILE"
            ;;
        *)
            echo "❌ Unknown format: $test_format"
            echo "Available formats: allure, junit, html, pretty, json"
            exit 1
            ;;
    esac
}

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
poetry install --no-dev

# Run API health check
echo "🏥 Running API health check..."
API_URL=${BASE_URL:-"https://your-wiremock-app.railway.app"}
if curl -f -s --max-time 10 "$API_URL" > /dev/null; then
    echo "✅ API is reachable: $API_URL"
else
    echo "⚠️  API may not be reachable: $API_URL"
    echo "Continuing with tests..."
fi

# Run tests
echo "🚀 Starting test execution..."
run_tests "$FORMAT"

# Check test results
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Tests completed successfully!"
    
    # Generate Allure report if format was allure
    if [ "$FORMAT" = "allure" ] && command -v allure &> /dev/null; then
        echo "📊 Generating Allure report..."
        allure generate reports/allure-results --clean -o reports/allure-report
        echo "📄 Allure report generated: reports/allure-report/index.html"
    fi
    
else
    echo ""
    echo "❌ Tests failed with exit code: $TEST_EXIT_CODE"
    echo "📝 Check log file: $LOG_FILE"
fi

echo ""
echo "📁 Test artifacts:"
echo "  - Logs: $LOG_FILE"
echo "  - Reports: reports/"

# Show summary
if [ -f "reports/junit/TESTS-*.xml" ]; then
    echo ""
    echo "📊 Test Summary:"
    grep -h "testsuite" reports/junit/TESTS-*.xml | head -1 | \
        sed -n 's/.*tests="\([0-9]*\)".*failures="\([0-9]*\)".*errors="\([0-9]*\)".*/Total: \1, Failures: \2, Errors: \3/p'
fi

exit $TEST_EXIT_CODE