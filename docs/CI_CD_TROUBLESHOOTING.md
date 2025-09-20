# CI/CD Troubleshooting Guide

## 🚨 Common Issues & Solutions

### 1. GitHub Actions Workflow Failures

#### ❌ Problem: "Secret not found" errors
```bash
Error: Secret RAILWAY_API_URL not found
```

**✅ Solution:**
1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add required secrets:
   - `RAILWAY_API_URL`: `https://wiremock-production.up.railway.app`
   - `API_AUTH_TOKEN`: `banking-api-key-2024`
3. Ensure secret names match exactly (case-sensitive)

#### ❌ Problem: Railway Wiremock connectivity issues
```bash
curl: (7) Failed to connect to wiremock-production.up.railway.app
```

**✅ Solution:**
1. **Verify Railway deployment:**
   ```bash
   curl https://wiremock-production.up.railway.app/__admin/health
   ```

2. **Check Railway service status:**
   - Login to Railway dashboard
   - Verify Wiremock service is running
   - Check deployment logs for errors

3. **Test locally:**
   ```bash
   # Test connectivity
   ping wiremock-production.up.railway.app

   # Test HTTP
   curl -I https://wiremock-production.up.railway.app
   ```

#### ❌ Problem: Tests fail with authentication errors
```bash
HTTP 401 Unauthorized
```

**✅ Solution:**
1. **Verify auth token in secrets:**
   ```bash
   # Check if token matches what Railway expects
   curl -H "Authorization: Bearer banking-api-key-2024" \
        https://wiremock-production.up.railway.app/customers/CUST001
   ```

2. **Update Wiremock mappings** if needed:
   ```json
   {
     "request": {
       "method": "GET",
       "urlPattern": "/customers/.*",
       "headers": {
         "Authorization": {
           "equalTo": "Bearer banking-api-key-2024"
         }
       }
     },
     "response": {
       "status": 200,
       "headers": {
         "Content-Type": "application/json"
       },
       "body": "{\"id\": \"CUST001\", \"name\": \"Test Customer\"}"
     }
   }
   ```

### 2. Branch Protection Issues

#### ❌ Problem: Cannot merge PR due to status checks
```bash
Required status checks must pass before merging
```

**✅ Solution:**
1. **Check failed status checks:**
   - Go to PR → **Checks** tab
   - Click on failed check to see details

2. **Common fixes:**
   ```bash
   # Code quality issues
   poetry run black .
   poetry run isort .
   poetry run flake8 features/

   # Test failures
   export ENVIRONMENT=test
   poetry run behave --tags=@smoke --format=pretty
   ```

3. **Update branch protection rules** if needed:
   - Settings → Branches → Edit rule for `main`
   - Adjust required status checks

#### ❌ Problem: Branch protection rules not applied
```bash
Repository setup workflow completed but protection not active
```

**✅ Solution:**
1. **Manual setup:**
   - Settings → Branches → Add rule
   - Branch name pattern: `main`
   - Enable required status checks

2. **Required checks to add:**
   - `Code Quality Checks`
   - `API Health Check`
   - `Smoke Tests (authentication)`
   - `Smoke Tests (accounts)`
   - `Smoke Tests (customers)`

### 3. Test Execution Problems

#### ❌ Problem: Tests timeout or hang
```bash
Test execution exceeds timeout limit
```

**✅ Solution:**
1. **Increase timeouts in environment config:**
   ```env
   REQUEST_TIMEOUT=30
   TIMEOUT=60
   PERFORMANCE_THRESHOLD_MS=5000
   ```

2. **Check Railway performance:**
   ```bash
   # Test response times
   time curl https://wiremock-production.up.railway.app/__admin/health
   ```

3. **Reduce concurrency:**
   ```env
   CONCURRENCY_LIMIT=1
   PARALLEL_EXECUTION=false
   ```

#### ❌ Problem: Environment variables not loaded
```bash
KeyError: 'BASE_URL'
```

**✅ Solution:**
1. **Check environment file loading:**
   ```python
   # In features/support/environment.py
   from dotenv import load_dotenv
   load_dotenv(f"environments/.env.{os.getenv('ENVIRONMENT', 'test')}")
   ```

2. **Verify environment files exist:**
   ```bash
   ls environments/
   # Should show: .env.test, .env.dev, etc.
   ```

3. **Set environment variable:**
   ```bash
   export ENVIRONMENT=test
   ```

### 4. Performance Issues

#### ❌ Problem: Tests run too slowly
```bash
Performance tests failing due to high response times
```

**✅ Solution:**
1. **Optimize Railway deployment:**
   - Check Railway resource usage
   - Consider upgrading Railway plan
   - Optimize Wiremock memory settings

2. **Adjust performance thresholds:**
   ```env
   PERFORMANCE_THRESHOLD_MS=10000  # Increase from 5000
   ```

3. **Monitor Railway metrics:**
   ```bash
   # Check Railway logs for performance issues
   railway logs
   ```

### 5. Artifact & Reporting Issues

#### ❌ Problem: No test reports generated
```bash
Allure reports directory is empty
```

**✅ Solution:**
1. **Check report generation:**
   ```bash
   # Verify reports directory exists
   mkdir -p reports/allure-results reports/junit

   # Run tests with proper reporting
   poetry run behave \
     --format=allure_behave.formatter:AllureFormatter \
     --outdir=reports/allure-results \
     --junit \
     --junit-directory=reports/junit
   ```

2. **Install required dependencies:**
   ```bash
   poetry install --with dev
   poetry add allure-behave
   ```

#### ❌ Problem: Artifacts not uploaded
```bash
Upload artifact failed: No files found
```

**✅ Solution:**
1. **Check file paths in workflow:**
   ```yaml
   - name: Upload test results
     uses: actions/upload-artifact@v4
     with:
       path: |
         reports/
         logs/
   ```

2. **Verify files exist before upload:**
   ```bash
   ls -la reports/
   ls -la logs/
   ```

## 🔍 Debugging Commands

### Local Testing
```bash
# Test Railway connectivity
curl -v https://wiremock-production.up.railway.app/__admin/health

# Test authentication
curl -H "Authorization: Bearer banking-api-key-2024" \
     https://wiremock-production.up.railway.app/customers/CUST001

# Run specific test suite
export ENVIRONMENT=test
export BASE_URL=https://wiremock-production.up.railway.app
poetry run behave --tags=@smoke --format=pretty features/authentication/

# Check environment loading
python -c "
import os
from dotenv import load_dotenv
load_dotenv('environments/.env.test')
print('BASE_URL:', os.getenv('BASE_URL'))
print('AUTH_TOKEN:', os.getenv('AUTH_TOKEN'))
"
```

### GitHub Actions Debugging
```bash
# Enable debug logging in workflow
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true

# Add debug steps to workflow
- name: Debug Environment
  run: |
    echo "Environment variables:"
    env | grep -E "(BASE_URL|AUTH_TOKEN|ENVIRONMENT)"
    echo "Current directory:"
    pwd
    echo "Directory contents:"
    ls -la
```

### Railway Debugging
```bash
# Check Railway service
railway status

# View Railway logs
railway logs --tail

# Test Railway service locally
railway run curl http://localhost:8080/__admin/health
```

## 📞 Getting Help

### 1. Check GitHub Actions Logs
- Go to **Actions** tab in repository
- Click on failed workflow run
- Expand failed steps to see detailed logs

### 2. Review Test Reports
- Download artifacts from GitHub Actions
- Open `reports/allure-report/index.html`
- Check `logs/failures/` for specific error details

### 3. Monitor Railway Service
- Check Railway dashboard for service health
- Review deployment logs
- Monitor resource usage

### 4. Community Support
- GitHub Issues: Report bugs and feature requests
- Railway Discord: Railway-specific deployment issues
- Behave Documentation: BDD framework questions

## 🚀 Best Practices

### 1. Regular Maintenance
```bash
# Update dependencies monthly
poetry update

# Review and rotate secrets quarterly
# Update performance thresholds based on Railway metrics
# Clean up old artifacts and logs
```

### 2. Monitoring Setup
```bash
# Set up Railway monitoring alerts
# Configure GitHub notifications for failed workflows
# Monitor test pass rates and performance trends
```

### 3. Documentation
```bash
# Keep this troubleshooting guide updated
# Document new issues and solutions
# Share knowledge with team members
```

## 📋 Emergency Procedures

### 1. Complete CI/CD Failure
1. **Disable workflows temporarily:**
   - .github/workflows/*.yml → Add `if: false` to jobs

2. **Verify Railway service:**
   ```bash
   curl https://wiremock-production.up.railway.app/__admin/health
   ```

3. **Test locally:**
   ```bash
   export ENVIRONMENT=test
   poetry run behave --tags=@smoke --format=pretty
   ```

4. **Re-enable workflows gradually:**
   - Start with single workflow
   - Verify success before enabling others

### 2. Railway Service Down
1. **Check Railway status page**
2. **Use local Wiremock as fallback:**
   ```bash
   docker run -p 8081:8080 wiremock/wiremock:latest
   # Update BASE_URL to http://localhost:8081
   ```

3. **Contact Railway support if needed**

Remember: **Always test changes in a feature branch before merging to main!**