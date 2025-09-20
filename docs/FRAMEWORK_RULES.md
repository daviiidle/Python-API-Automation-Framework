# 🏦 Banking API BDD Framework - Development Rules & Guidelines

> **Essential guide for all developers working on this Banking API BDD test framework**

---

## 📋 **Table of Contents**
- [Logging Standards](#-logging-standards)
- [Step Definition Rules](#-step-definition-rules)
- [File Structure Standards](#-file-structure-standards)
- [Error Handling Guidelines](#-error-handling-guidelines)
- [Data Management Rules](#-data-management-rules)
- [Performance & Metrics](#-performance--metrics)
- [Code Quality Standards](#-code-quality-standards)
- [Testing Best Practices](#-testing-best-practices)

---

## 🖥️ **Cross-Platform Compatibility Rules**

### **CRITICAL RULE: No Emoji Characters in Production Code**
For Windows compatibility and terminal support, all emoji characters have been replaced with plain text prefixes:

```python
# ❌ WRONG - Emoji characters cause UnicodeEncodeError on Windows
context.logger.info("🔍 Checking API availability...")

# ✅ CORRECT - Plain text prefixes work everywhere  
context.logger.info("[API] Checking API availability...")
```

### **Standard Text Prefixes**
| Prefix | Usage | Old Emoji |
|--------|-------|-----------|
| `[API]` | API operations | 🔍, 🌐 |
| `[SUCCESS]` | Success indicators | ✅, 🎉 |
| `[ERROR]` | Error messages | ❌, 💥 |
| `[TIMEOUT]` | Timeout issues | ⏰ |
| `[CONNECTION]` | Connection errors | 🔌 |
| `[RESPONSE]` | API responses | 📡 |
| `[TIME]` | Response times | ⏱️ |
| `[HEADERS]` | HTTP headers | 📋 |
| `[BODY]` | Request/response body | 📝 |
| `[WARNING]` | Warnings | ⚠️ |
| `[AUTH]` | Authentication | 🔑 |
| `[DATA]` | Data generation | 🎲 |
| `[ENV]` | Environment info | 🌍 |

---

## 🗄️ **Logging Standards**

### **CRITICAL RULE: Never Use `print()` Statements**
```python
# ❌ WRONG - Never do this
print("Starting test")

# ✅ CORRECT - Always use context.logger
context.logger.info("🧪 Starting test scenario")
```

### **Logging Hierarchy & Usage**

#### **ERROR Level - `context.logger.error()`**
- Use for: Test failures, assertion errors, exceptions
- Format: `❌ <Action> FAILED: <details>`
- Example: `context.logger.error("❌ Status code assertion FAILED: Expected 200, got 500")`

#### **WARNING Level - `context.logger.warning()`**
- Use for: Non-critical issues, missing optional data
- Format: `⚠️ <Issue description>`
- Example: `context.logger.warning("⚠️ Missing WWW-Authenticate header")`

#### **INFO Level - `context.logger.info()`**
- Use for: Major test milestones, API calls, assertions
- Format: `🎯 <Action> or ✅ <Action> PASSED`
- Examples:
  ```python
  context.logger.info("🔄 Sending GET request to: /accounts/123")
  context.logger.info("✅ Status code assertion PASSED: 200")
  ```

#### **DEBUG Level - `context.logger.debug()`**
- Use for: Detailed request/response data, headers, internal state
- Format: `📋 <Type>: <data>`
- Examples:
  ```python
  context.logger.debug(f"📋 Request Headers: {dict(headers)}")
  context.logger.debug(f"📄 Response Body: {response.text[:500]}...")
  ```

### **Mandatory Logging Emojis**
```python
🏦 Framework initialization
🧪 Test scenario actions
🔄 HTTP requests (GET, POST, PUT, DELETE)
📡 HTTP responses
🎯 Verification/assertion start
✅ Success/pass
❌ Failure/error
⚠️  Warning/non-critical issue
🔍 Checking/verifying
📊 Status codes, metrics
⏱️  Timing/performance
🌐 URLs, endpoints
📋 Headers, metadata
📄 Request/response bodies
🔐 Authentication
🔑 API keys/tokens (masked)
💥 Exceptions
```

### **Sensitive Data Masking**
```python
# ✅ ALWAYS mask sensitive data
auth_token = "banking-api-key-2024"
masked_token = f"{'*' * (len(auth_token) - 4)}{auth_token[-4:]}"
context.logger.info(f"🔑 Auth Token: {masked_token}")
```

---

## 🧩 **Step Definition Rules**

### **File Organization**
- `common_steps.py` - Generic HTTP operations, basic assertions
- `auth_steps.py` - Authentication and security testing
- `data_steps.py` - Data generation and table-driven tests
- `<service>_steps.py` - Service-specific complex operations

### **CRITICAL: Duplicate Step Prevention**
**ALWAYS check for existing step definitions before adding new ones:**

```bash
# Search for existing step definitions before adding new ones
grep -r "@given.*your_step_text" features/steps/
grep -r "@when.*your_step_text" features/steps/
grep -r "@then.*your_step_text" features/steps/
```

**Common step definitions that already exist:**
- ✅ `@then('the response should be valid JSON')` - in common_steps.py:582
- ✅ `@then('the response should contain "{key}"')` - in common_steps.py:523
- ✅ `@then('the response "{key}" should be "{value}"')` - DOES NOT EXIST - can be added
- ✅ `@when('I send a POST request to "{endpoint}" with data')` - in common_steps.py:644
- ✅ `@then('the response should contain the correlation ID')` - in common_steps.py:634
- ✅ `@then('I should receive an unauthorized error')` - in auth_steps.py
- ✅ `@given('I have no authentication token')` - in auth_steps.py

**Before adding ANY step definition:**
1. Search existing files for similar steps
2. Check if the step can be parameterized instead of duplicated
3. If adding a new step, add a comment explaining why it's needed
4. Update this documentation with the new step location

### **Step Definition Standards**

#### **Mandatory Elements in Every Step**
```python
@given('step description')
def step_function_name(context: Context, param: str):
    """Clear docstring describing what this step does."""
    
    # 1. ALWAYS start with logging what we're doing
    context.logger.info(f"🎯 Action description: {param}")
    
    # 2. Validate prerequisites
    if not hasattr(context, 'required_attribute'):
        context.logger.error("❌ Missing required prerequisite")
        raise AssertionError("Prerequisite not met")
    
    # 3. Perform action with detailed logging
    try:
        # Implementation here
        context.logger.info("✅ Action completed successfully")
    except Exception as e:
        context.logger.error(f"💥 Action failed: {e}")
        context.last_error = str(e)
        raise
```

#### **HTTP Request Steps Must Include**
```python
@when('I send a GET request to "{endpoint}"')
def step_get_request(context: Context, endpoint: str):
    # Log request details
    context.logger.info(f"🔄 Sending GET request to: {endpoint}")
    context.logger.debug(f"🌐 Full URL: {full_url}")
    context.logger.debug(f"📋 Request Headers: {dict(headers)}")
    
    try:
        start_time = time.time()
        response = requests.get(full_url, headers=headers, timeout=30)
        response_time = time.time() - start_time
        
        # Update metrics
        if hasattr(context, 'test_metrics'):
            context.test_metrics['api_calls'] += 1
            context.test_metrics['total_response_time'] += response_time
        
        # Log response
        context.logger.info(f"📡 GET Response: {response.status_code}")
        context.logger.info(f"⏱️  Response Time: {response_time:.3f}s")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"⏰ GET request to {endpoint} timed out")
        raise AssertionError(f"Request timeout")
```

#### **Assertion Steps Must Include**
```python
@then('assertion description')
def step_assert_something(context: Context, expected: str):
    context.logger.info(f"🎯 Verifying: {assertion_description}")
    
    # Check prerequisites
    if not hasattr(context, 'response'):
        context.logger.error("❌ No response available")
        raise AssertionError("No response available")
    
    # Perform assertion with detailed logging
    if assertion_passes:
        context.logger.info(f"✅ Assertion PASSED: {details}")
    else:
        context.logger.error(f"❌ Assertion FAILED: {details}")
        # Log debugging information
        context.logger.debug(f"📄 Actual data: {actual_data}")
        raise AssertionError(f"Assertion failed: {details}")
```

---

## 📁 **File Structure Standards**

### **Directory Rules**
- `features/` - BDD feature files, organized by service
- `steps/` - Step definition files
- `support/` - Framework utilities and helpers
- `environments/` - Environment configuration files
- `logs/` - Test execution logs (auto-created)
- `reports/` - Test reports and results

### **Import Standards**
```python
# Standard library imports first
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Third-party imports
import requests
from behave import given, when, then, step
from behave.runner import Context

# Local imports (if any)
from support.utils.data_generator import generate_test_data
```

---

## ⚠️ **Error Handling Guidelines**

### **Exception Handling Pattern**
```python
try:
    # Risky operation
    result = perform_operation()
    context.logger.info("✅ Operation successful")
    
except requests.exceptions.Timeout:
    context.logger.error("⏰ Operation timed out")
    context.last_error = "Timeout"
    raise AssertionError("Operation timed out")
    
except requests.exceptions.ConnectionError as e:
    context.logger.error(f"🔌 Connection error: {e}")
    context.last_error = str(e)
    raise AssertionError(f"Connection error: {e}")
    
except Exception as e:
    context.logger.error(f"💥 Unexpected error: {e}")
    context.last_error = str(e)
    raise
```

### **Assertion Error Messages**
```python
# ✅ GOOD - Clear, actionable error messages
raise AssertionError(f"Expected status 200, got {actual_status}. Response: {response.text[:200]}...")

# ❌ BAD - Vague error messages
raise AssertionError("Status code wrong")
```

---

## 📊 **Data Management Rules**

### **Environment Variable Usage**
```python
# ✅ NEVER hardcode URLs, tokens, or configuration
# ❌ WRONG - Never do this
base_url = "https://hardcoded-url.com"
auth_token = "hardcoded-token"

# ✅ CORRECT - Always use environment variables
base_url = context.base_url  # Loaded from .env files
auth_token = context.auth_token  # From environment
timeout = context.request_timeout  # From environment
```

### **Test Data Generation**
```python
# ✅ Always log data generation
context.logger.info(f"🎲 Generating test data for: {data_type}")
test_data = generate_data(data_type)
context.logger.debug(f"📄 Generated data: {json.dumps(test_data, indent=2)}")
```

### **Context Data Storage**
```python
# Standard context attributes to use:
context.response              # Last HTTP response
context.last_response         # Alias for response
context.auth_headers          # Authentication headers (from environment)
context.base_url             # API base URL (from environment)
context.auth_token           # Authentication token (from environment)
context.environment          # Current test environment (dev/railway/staging/prod)
context.request_timeout      # Request timeout (from environment)
context.performance_threshold_ms  # Performance threshold (from environment)
context.test_data            # Generated test data
context.scenario_metrics     # Scenario-level metrics
context.last_error          # Last error message
```

### **Environment Configuration Loading**
```python
# ✅ Environment variables are automatically loaded from .env files
# Files checked in order:
# 1. environments/.env.{ENVIRONMENT}  (e.g., .env.railway, .env.dev)
# 2. System environment variables
# 3. Fallback defaults

# Standard environment variables used:
BASE_URL=http://wiremock-production.up.railway.app
AUTH_TOKEN=banking-api-key-2024
REQUEST_TIMEOUT=10
PERFORMANCE_THRESHOLD_MS=2000
ENVIRONMENT=railway
```

---

## ⚡ **Performance & Metrics**

### **Mandatory Metrics Tracking**
```python
# In HTTP request steps, ALWAYS update metrics:
if hasattr(context, 'test_metrics'):
    context.test_metrics['api_calls'] += 1
    context.test_metrics['total_response_time'] += response_time

if hasattr(context, 'scenario_metrics'):
    context.scenario_metrics['api_calls'] += 1
    context.scenario_metrics['total_response_time'] += response_time
```

### **Response Time Logging**
```python
# ALWAYS log response times
start_time = time.time()
response = requests.get(url, headers=headers)
response_time = time.time() - start_time
context.logger.info(f"⏱️  Response Time: {response_time:.3f}s")
```

---

## 🔍 **Code Quality Standards**

### **Type Hints (Required)**
```python
from typing import Dict, Any, Optional
from behave.runner import Context

def step_function(context: Context, endpoint: str) -> None:
    """Function with proper type hints."""
```

### **Docstrings (Required)**
```python
def step_function(context: Context, endpoint: str):
    """
    Clear description of what this step does.
    
    Args:
        context: Behave context object
        endpoint: API endpoint path
    """
```

### **Variable Naming**
```python
# ✅ GOOD - Clear, descriptive names
response_time = time.time() - start_time
auth_headers = get_auth_headers()
base_url = context.base_url

# ❌ BAD - Unclear names
t = time.time() - s
h = get_headers()
url = context.url
```

---

## 🧪 **Testing Best Practices**

### **Feature File Standards**
```gherkin
@api @banking @service_name @test_type
Feature: Clear feature description
  As a [user type]
  I want to [action]
  So that [benefit]

  Background:
    Given the banking API is available
    And I have valid authentication credentials

  @smoke @happy_path
  Scenario: Clear scenario description
    Given I generate test data for "service"
    When I send a POST request to "/endpoint"
    Then the response status code should be 201
    And the response should be valid JSON
```

### **Tag Usage Standards**
- `@api` - All API tests
- `@banking` - Banking domain tests
- `@smoke` - Critical path tests
- `@regression` - Full regression suite
- `@performance` - Performance tests
- `@security` - Security tests
- `@error_handling` - Error scenario tests
- `@dynamic_data` - Tests using generated data

### **Scenario Organization**
- One scenario = One test case
- Maximum 10 steps per scenario
- Use Background for common setup
- Group related scenarios in same feature file

---

## 🚫 **What NOT To Do**

### **Forbidden Practices**
```python
# ❌ NEVER use print statements
print("Test started")

# ❌ NEVER hardcode URLs, tokens, or configuration
base_url = "https://hardcoded-url.com"
auth_token = "banking-api-key-2024"  # Use env vars instead
timeout = 30  # Use context.request_timeout instead

# ❌ NEVER hardcode environment-specific values
if environment == "prod":
    url = "https://prod-api.com"  # Use .env files instead

# ❌ NEVER ignore exceptions
try:
    response = requests.get(url)
except:
    pass  # This hides errors

# ❌ NEVER use generic exception handling
except Exception:
    pass  # Too broad, masks specific issues

# ❌ NEVER skip logging for important actions
response = requests.post(url, data=data)  # Missing request logging

# ❌ NEVER bypass environment configuration loading
# Always ensure setup_fallback_logger(context) or environment.py runs first
```

### **CRITICAL: Configuration Management Rules**
```python
# ✅ ALWAYS load configuration from environment
if not hasattr(context, 'logger'):
    setup_fallback_logger(context)  # This loads .env files

# ✅ ALWAYS use context variables for configuration
base_url = context.base_url         # ✅ From environment
timeout = context.request_timeout   # ✅ From environment
headers = context.auth_headers       # ✅ From environment

# ❌ NEVER hardcode configuration values
base_url = "https://fixed-url.com"   # ❌ Wrong!
timeout = 30                         # ❌ Wrong!
```

---

## 📝 **Checklist for New Step Definitions**

Before committing any step definition, verify:

- [ ] Proper logging with emojis at start of step
- [ ] Type hints for all parameters
- [ ] Clear docstring
- [ ] Input validation and error handling
- [ ] Detailed logging for all actions
- [ ] Metrics tracking for HTTP requests
- [ ] Response time logging for API calls
- [ ] Proper exception handling with specific messages
- [ ] Success/failure logging
- [ ] No `print()` statements
- [ ] Sensitive data masking

---

## 🔄 **Update Guidelines**

### **When modifying this framework:**
1. **Always** add comprehensive logging
2. **Never** break existing logging patterns
3. **Always** update this documentation if adding new rules
4. **Test** all changes with actual API calls
5. **Review** logs to ensure they're helpful for debugging

### **For new contributors:**
1. Read this entire document before coding
2. Follow existing patterns in the codebase
3. Add logging for every action
4. Test with real API endpoints
5. Ask questions if rules are unclear

---

## 🎯 **Framework Philosophy**

> **"Every action should be traceable through logs. Every failure should be debuggable through the log file. Every success should be verifiable through metrics."**

This framework prioritizes:
1. **Transparency** - Complete visibility into test execution
2. **Debuggability** - Easy troubleshooting through comprehensive logs
3. **Reliability** - Consistent error handling and reporting
4. **Performance** - Metrics tracking for all operations
5. **Maintainability** - Clear code standards and documentation

---

**Remember: A senior SDET framework should be so well-logged that you can debug any issue just by reading the log file! 📋✨**