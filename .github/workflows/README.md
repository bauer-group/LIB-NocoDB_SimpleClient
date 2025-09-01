# GitHub Actions Workflows

This directory contains the CI/CD workflows for the NocoDB Simple Client project.

## Workflows Overview

### 1. `python-automatic-release.yml`
**Purpose**: Automated releases on main branch
**Trigger**: Push to `main` branch
**Tests**: Unit tests only (fast, no external dependencies)
**Dependencies**: None (uses mocks)

### 2. `feature-test.yml`
**Purpose**: Comprehensive testing on feature branches
**Trigger**: Push to `feature-*` branches
**Tests**: Unit tests + Integration tests with live NocoDB
**Dependencies**: Automatic NocoDB setup with SQLite

## Workflow Details

### Release Workflow (`python-automatic-release.yml`)
- **Fast execution** (~2-3 minutes)
- **No external dependencies**
- **All Python versions** (3.8-3.12)
- **Unit tests only** via `--ci` flag
- **Automatic versioning** and PyPI publishing

### Feature Testing Workflow (`feature-test.yml`)

#### Job 1: Unit Tests
- **Matrix**: Python 3.9, 3.11, 3.12
- **Duration**: ~2-4 minutes
- **Dependencies**: None (mocked)
- **Purpose**: Fast feedback on basic functionality

#### Job 2: Integration Tests
- **Setup**: Automatic NocoDB instance with SQLite
- **User Creation**: Automated admin user setup
- **API Token**: Dynamic token generation
- **Tests**: Full integration test suite
- **Duration**: ~8-12 minutes
- **Environment Variables**: Automatically configured

#### Job 3: Performance Tests (Optional)
- **Trigger**: PR label `test-performance`
- **Setup**: Optimized NocoDB instance
- **Tests**: Performance benchmarks
- **Reduced Dataset**: CI-appropriate test sizes

## NocoDB Setup Process

The feature workflow automatically:

1. **Starts NocoDB Container**:
   ```bash
   docker run -d --name nocodb-test \
     -p 8080:8080 \
     -e NC_DB="sqlite3://data/nc.db" \
     -e NC_AUTH_JWT_SECRET="test-jwt-secret-$(date +%s)" \
     -e NC_DISABLE_TELE=true \
     nocodb/nocodb:latest
   ```

2. **Creates Admin User**:
   ```bash
   curl -X POST /api/v1/auth/user/signup \
     -d '{"email":"test@example.com","password":"TestPassword123!"}'
   ```

3. **Gets API Token**:
   ```bash
   curl -X POST /api/v1/auth/user/signin \
     -d '{"email":"test@example.com","password":"TestPassword123!"}'
   ```

4. **Configures Environment**:
   ```bash
   NOCODB_BASE_URL=http://localhost:8080
   NOCODB_TOKEN=$TOKEN
   TEST_TABLE_PREFIX=gh_test_
   MAX_FILE_SIZE_MB=1
   ```

## Environment Configuration

### Automatic Environment Variables
The workflow automatically configures:

| Variable | Value | Description |
|----------|-------|-------------|
| `NOCODB_BASE_URL` | `http://localhost:8080` | NocoDB instance URL |
| `NOCODB_TOKEN` | `${{ steps.setup-nocodb.outputs.token }}` | Dynamic API token |
| `TEST_TABLE_PREFIX` | `gh_test_` | Prefix for test tables |
| `CLEANUP_TEST_DATA` | `true` | Auto-cleanup enabled |
| `RUN_INTEGRATION_TESTS` | `true` | Enable integration tests |
| `TEST_TIMEOUT` | `60` | Extended timeout for CI |
| `MAX_FILE_SIZE_MB` | `1` | File upload limit |
| `PERFORMANCE_TEST_RECORDS` | `50` | Reduced for CI speed |
| `BULK_TEST_BATCH_SIZE` | `10` | Small batches for CI |

### Error Handling & Debugging

#### Automatic Debugging on Failure:
```bash
# Show NocoDB logs
docker logs nocodb-test

# Show container status
docker ps -a

# Test API connectivity
curl -v http://localhost:8080/api/v1/health
```

#### Cleanup on Success/Failure:
```bash
docker stop nocodb-test || true
docker rm nocodb-test || true
rm -rf ./nocodb-data || true
```

## Usage Examples

### Triggering Feature Tests
```bash
# Push to feature branch triggers automatic testing
git checkout -b feature/new-functionality
git push origin feature/new-functionality
```

### Adding Performance Tests
```bash
# Add label to PR to trigger performance tests
gh pr edit --add-label "test-performance"
```

### Local Testing Equivalent
```bash
# Same tests locally
python scripts/run-all.py --integration   # Integration tests
python scripts/run-all.py --performance   # Performance tests
python scripts/run-all.py --all-tests     # Everything
```

## Troubleshooting

### Common Issues

1. **NocoDB startup timeout**:
   - Increased timeout to 120s
   - Multiple health check methods
   - Fallback token generation

2. **API token extraction failure**:
   - Multiple extraction methods
   - Fallback token generation
   - Graceful error handling

3. **Test data conflicts**:
   - Unique table prefixes (`gh_test_`, `perf_test_`)
   - Automatic cleanup
   - Isolated containers per job

### Debug Steps

1. **Check workflow logs** in GitHub Actions
2. **Review NocoDB container logs** (shown on failure)
3. **Test API endpoints manually** using curl commands
4. **Run locally** with same environment variables

## Performance Considerations

### Optimizations Applied:
- **Reduced Python matrix** for feature tests (3 versions vs 5)
- **SQLite database** (faster than PostgreSQL/MySQL)
- **Disabled telemetry** (`NC_DISABLE_TELE=true`)
- **Reduced test datasets** for CI environment
- **Parallel job execution** where possible
- **Efficient cleanup** to minimize resource usage

### Expected Durations:
- **Unit tests**: 2-4 minutes per Python version
- **Integration tests**: 8-12 minutes total
- **Performance tests**: 10-15 minutes (when enabled)
- **Total feature workflow**: ~15-20 minutes
