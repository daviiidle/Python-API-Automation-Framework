# GitHub Repository Setup Guide

## Required GitHub Secrets Configuration

To enable CI/CD with your Railway Wiremock deployment, you need to configure the following secrets in your GitHub repository.

### 🔧 How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

### 📋 Required Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `RAILWAY_API_URL` | `https://wiremock-production.up.railway.app` | Your Railway Wiremock deployment URL |
| `API_AUTH_TOKEN` | `banking-api-key-2024` | Default authentication token for tests |
| `RAILWAY_API_TOKEN` | `banking-api-key-2024` | Railway-specific auth token (can be same as above) |

### 🔧 Optional Secrets (for multi-environment setup)

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `STAGING_API_URL` | `https://your-staging-api.com` | Staging environment URL (if you have one) |
| `STAGING_API_TOKEN` | `staging-auth-token` | Staging authentication token |
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/...` | Slack webhook for notifications (optional) |

## Repository Variables Configuration

### 🔧 How to Add Variables

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click the **Variables** tab
4. Click **New repository variable**
5. Add each variable below

### 📋 Repository Variables

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `DEFAULT_TEST_ENVIRONMENT` | `railway` | Default environment for tests |
| `PYTHON_VERSION` | `3.11` | Python version for CI/CD |
| `PERFORMANCE_THRESHOLD_MS` | `5000` | Performance test threshold in milliseconds |
| `CONCURRENCY_LIMIT` | `3` | Maximum concurrent test executions |

## Branch Protection Rules

### 🛡️ Recommended Branch Protection Settings

1. Go to **Settings** → **Branches**
2. Click **Add rule** for `main` branch
3. Configure these settings:

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- Required checks:
  - `Code Quality Checks`
  - `API Health Check`
  - `Smoke Tests (authentication)`
  - `Smoke Tests (accounts)`
  - `Smoke Tests (customers)`
  - `Security Scan`
  - `Code Coverage`

#### Additional Protection Rules
- ✅ **Require pull request reviews before merging**
- ✅ **Dismiss stale PR approvals when new commits are pushed**
- ✅ **Require review from code owners** (optional)
- ✅ **Restrict pushes that create files to administrators**
- ✅ **Allow force pushes** (unchecked)
- ✅ **Allow deletions** (unchecked)

## Environment-Specific Secrets (Advanced)

If you want to use GitHub Environments for better organization:

### 🌍 Create Environments

1. Go to **Settings** → **Environments**
2. Create these environments:
   - `development`
   - `railway`
   - `staging`
   - `production`

### 🔐 Environment-Specific Secrets

#### Railway Environment
- `API_URL`: `https://wiremock-production.up.railway.app`
- `AUTH_TOKEN`: `banking-api-key-2024`

#### Staging Environment (if applicable)
- `API_URL`: Your staging URL
- `AUTH_TOKEN`: Your staging token

## Verification Steps

### ✅ Test Your Setup

1. **Create a test PR** to verify workflows trigger correctly
2. **Check Actions tab** to see if workflows run without secret errors
3. **Review workflow logs** for proper API connectivity
4. **Verify notifications** work if configured

### 🔍 Troubleshooting

**Common Issues:**

1. **Secret not found errors**
   - Verify secret names match exactly (case-sensitive)
   - Check secret is in correct repository/environment

2. **API connectivity issues**
   - Verify Railway URL is accessible
   - Test manually: `curl https://wiremock-production.up.railway.app/__admin/health`

3. **Permission errors**
   - Ensure GitHub Actions has permission to read secrets
   - Check repository settings allow Actions

## Quick Setup Commands

Run these commands to verify your Railway deployment:

```bash
# Test Railway Wiremock health
curl https://wiremock-production.up.railway.app/__admin/health

# Test authentication
curl -H "Authorization: Bearer banking-api-key-2024" \
     https://wiremock-production.up.railway.app/customers/CUST001

# Check available mappings
curl https://wiremock-production.up.railway.app/__admin/mappings
```

## Next Steps

After configuring secrets:

1. **Push changes** to trigger workflows
2. **Create a test PR** to verify PR validation workflow
3. **Check nightly regression** runs at scheduled time
4. **Monitor test results** and adjust thresholds as needed
5. **Set up notifications** for team collaboration

## Security Best Practices

- 🔒 **Never commit secrets** to repository
- 🔍 **Regularly rotate tokens** and update secrets
- 👥 **Limit secret access** to necessary team members
- 📝 **Document secret usage** for team reference
- 🚨 **Monitor for secret exposure** in logs