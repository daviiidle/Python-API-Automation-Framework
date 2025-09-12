#!/bin/bash

# Banking API BDD Framework Setup Script
# This script sets up the development environment

set -e

echo "🏦 Banking API BDD Framework Setup"
echo "=================================="

# Check if Python 3.11+ is installed
echo "🐍 Checking Python version..."
if ! python3 --version | grep -E "3\.(11|12)" > /dev/null; then
    echo "❌ Python 3.11+ is required. Please install Python 3.11 or newer."
    exit 1
fi
echo "✅ Python version is compatible"

# Check if Poetry is installed
echo "📦 Checking Poetry installation..."
if ! command -v poetry &> /dev/null; then
    echo "🔧 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "✅ Poetry installed successfully"
    echo "⚠️  Please restart your terminal or run: source ~/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
fi

# Configure Poetry
echo "⚙️  Configuring Poetry..."
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true

# Install dependencies
echo "📚 Installing project dependencies..."
poetry install

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p {reports/allure-results,reports/junit,logs,test_data/dev,test_data/staging,test_data/railway,test_data/ci}

# Set up pre-commit hooks
echo "🔨 Setting up pre-commit hooks..."
poetry run pre-commit install

# Validate installation
echo "✅ Validating installation..."
poetry run python -c "
import behave
import requests
import faker
import pydantic
print('✅ All core dependencies are working')
"

# Create sample test data
echo "📄 Creating sample test data files..."
cat > test_data/dev/sample_customers.json << EOF
{
  "valid_customer": {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+61412345678",
    "dob": "1990-01-15"
  },
  "invalid_customer": {
    "firstName": "",
    "lastName": "Doe",
    "email": "invalid-email",
    "phone": "123"
  }
}
EOF

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore file..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Test Reports
reports/
logs/
*.log
.allure/
.pytest_cache/

# Environment Files
.env
.env.local
.env.*.local

# Temporary Files
*.tmp
*.temp
.tmp/

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
EOF
fi

# Create README if it doesn't exist
if [ ! -f "README.md" ]; then
    echo "📖 Creating README.md..."
    cat > README.md << 'EOF'
# Banking API BDD Test Framework

A comprehensive BDD test framework for Banking API testing using Behave, with dynamic data generation and CI/CD integration.

## 🚀 Quick Start

1. **Setup Environment:**
   ```bash
   ./scripts/setup_environment.sh
   ```

2. **Run Smoke Tests:**
   ```bash
   ./scripts/run_tests.sh test @smoke pretty
   ```

3. **Run Full Regression:**
   ```bash
   ./scripts/run_tests.sh railway @regression allure
   ```

## 🧪 Test Execution

### Local Testing
```bash
# Smoke tests
poetry run behave --tags=@smoke

# Regression tests with Allure reporting
poetry run behave --tags=@regression --format=allure_behave.formatter:AllureFormatter --outdir=reports/allure-results

# Specific service tests
poetry run behave --tags=@accounts features/accounts/
```

### Docker Testing
```bash
# Smoke tests
docker-compose --profile smoke up

# Full regression
docker-compose --profile regression up

# View Allure reports
docker-compose --profile reporting up -d
# Open http://localhost:5050
```

## 📊 Test Coverage

- **450+ BDD Scenarios** across all banking services
- **Dynamic Data Generation** using Faker
- **Multiple Environments** (dev, staging, railway, prod)
- **Performance Testing** with concurrent execution
- **Security Testing** with authentication scenarios
- **Integration Testing** with end-to-end workflows

## 🏗️ Architecture

```
├── features/               # BDD feature files
│   ├── accounts/          # Account management features
│   ├── customers/         # Customer management features
│   ├── bookings/          # Booking management features
│   ├── loans/             # Loan management features
│   ├── term_deposits/     # Term deposit features
│   ├── authentication/   # Auth & security features
│   └── integration/       # End-to-end workflows
├── steps/                 # Step definitions
├── support/               # Test utilities and helpers
│   ├── clients/          # API clients
│   ├── config/           # Configuration management
│   └── utils/            # Utilities and data generators
├── environments/          # Environment configurations
└── .github/workflows/     # CI/CD pipelines
```

## 🔧 Configuration

Environment configurations are stored in `environments/` directory:
- `.env.dev` - Development environment
- `.env.staging` - Staging environment
- `.env.railway` - Railway production environment
- `.env.test` - CI/CD testing environment

## 📈 Reporting

- **Allure Reports** - Rich HTML reports with screenshots and logs
- **JUnit XML** - CI/CD compatible test results
- **Performance Metrics** - Response time and throughput analysis
- **GitHub Actions Integration** - Automated test execution and reporting

## 🚀 CI/CD Integration

The framework includes GitHub Actions workflows for:
- **PR Validation** - Smoke tests and code quality checks
- **Nightly Regression** - Full test suite execution
- **Performance Testing** - Load and stress testing
- **Security Testing** - Authentication and authorization testing

## 🤝 Contributing

1. Run setup: `./scripts/setup_environment.sh`
2. Create feature branch
3. Add tests and features
4. Run tests locally: `./scripts/run_tests.sh`
5. Create pull request

Tests will automatically run on PR creation and provide feedback.
EOF
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Update environment files in environments/ with your API URLs and tokens"
echo "2. Run smoke tests: ./scripts/run_tests.sh test @smoke"
echo "3. Run full tests: ./scripts/run_tests.sh railway @regression allure"
echo ""
echo "📚 Documentation: README.md"
echo "🐳 Docker: docker-compose --profile smoke up"
echo ""