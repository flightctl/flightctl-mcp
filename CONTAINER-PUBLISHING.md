# Container Publishing Setup

This document explains how to set up automated container building and publishing to quay.io for the FlightCtl MCP Server.

## Overview

The repository is configured with GitHub Actions that automatically:
- ✅ Run comprehensive tests (linting, type checking, unit tests)
- 🔒 Scan container images for security vulnerabilities  
- 🏗️ Build multi-platform container images (linux/amd64, linux/arm64)
- 📦 Push images to `quay.io/flightctl/flightctl-mcp:latest`
- 🏷️ Tag images with branch name and commit SHA

## Workflow Triggers

The container publishing workflow (`.github/workflows/container-publish.yml`) triggers on:
- **Push to main branch**: Automatic build and push after every merged commit
- **Manual dispatch**: Can be triggered manually from the GitHub Actions tab

## Required Secrets

To enable container publishing, the following GitHub repository secrets must be configured:

### 1. QUAY_USERNAME
- **Description**: Username for quay.io authentication
- **Value**: Your quay.io username or robot account name
- **Example**: `flightctl+github_actions` (robot account format)

### 2. QUAY_PASSWORD  
- **Description**: Password or token for quay.io authentication
- **Value**: Your quay.io password or robot account token
- **Security**: Use a robot account token rather than personal password

## Setting Up Secrets

### Option 1: Using quay.io Robot Accounts (Recommended)

1. **Create Robot Account**:
   - Go to quay.io → Account Settings → Robot Accounts
   - Click "Create Robot Account"
   - Name: `github_actions` 
   - Permissions: `Write` to `flightctl/flightctl-mcp` repository

2. **Configure GitHub Secrets**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions
   - Add repository secrets:
     ```
     QUAY_USERNAME: flightctl+github_actions
     QUAY_PASSWORD: <robot-account-token>
     ```

### Option 2: Using Personal Account

1. **Get Credentials**:
   - Username: Your quay.io username
   - Password: Your quay.io password (consider using an access token)

2. **Configure GitHub Secrets**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions  
   - Add repository secrets:
     ```
     QUAY_USERNAME: <your-username>
     QUAY_PASSWORD: <your-password>
     ```

## Workflow Features

### 🔄 Test Integration
- Container builds only run **after** all tests pass
- Ensures code quality before publishing
- Failed tests prevent publishing broken images

### 🔒 Security Scanning
- **Trivy** scans for vulnerabilities in container images
- Results uploaded to GitHub Security tab
- Critical vulnerabilities are highlighted in pull requests

### 🏗️ Multi-Platform Builds
- Builds for both `linux/amd64` and `linux/arm64`
- Uses Docker Buildx for efficient cross-platform compilation
- Supports running on both x86 and ARM infrastructure

### 🏷️ Smart Tagging
The workflow creates multiple tags for each build:
- `latest` - Always points to the most recent main branch build
- `main-<sha>` - Specific commit reference (e.g., `main-abc1234`)
- `main` - Branch reference

### ⚡ Build Caching
- Uses GitHub Actions cache for faster builds
- Reuses layers between builds to minimize build time
- Automatically manages cache lifecycle

## Image Usage

Once published, the container can be used:

```bash
# Pull the latest image
docker pull quay.io/flightctl/flightctl-mcp:latest

# Run with default streamable-http transport
docker run -p 8000:8000 quay.io/flightctl/flightctl-mcp:latest

# Run with environment configuration  
docker run -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  -e API_BASE_URL=https://your-flightctl.example.com \
  quay.io/flightctl/flightctl-mcp:latest
```

## Monitoring

### GitHub Actions
- View workflow runs in the "Actions" tab
- Monitor build status and logs
- Review security scan results

### quay.io Dashboard
- Track image pulls and usage statistics
- View vulnerability scan results
- Manage repository permissions

### GitHub Security Tab
- View Trivy security scan results
- Track vulnerability trends over time
- Get alerts for new security issues

## Troubleshooting

### Authentication Failures
```
Error: failed to authorize: authentication required
```
**Solution**: Verify `QUAY_USERNAME` and `QUAY_PASSWORD` secrets are correctly set

### Build Failures
```
Error: failed to build: context deadline exceeded
```
**Solution**: Check Containerfile syntax and dependencies in requirements.txt

### Permission Errors
```
Error: failed to push: access denied
```
**Solution**: Ensure robot account has `Write` permissions to the repository

### Security Scan Failures
- **High/Critical vulnerabilities**: Update base image or dependencies
- **False positives**: Add exceptions in `.trivyignore` file
- **Scan timeouts**: Increase timeout in workflow configuration

## Manual Workflow Execution

To manually trigger a container build:

1. Go to GitHub repository → Actions tab
2. Select "Build and Push Container Image" workflow
3. Click "Run workflow" button
4. Choose branch (usually `main`)
5. Click "Run workflow" to start

This is useful for:
- Testing changes to the container workflow
- Rebuilding after fixing security vulnerabilities
- Creating builds from specific commits or branches 