# InstaBids Testing Guide

## Overview

This guide covers the comprehensive testing infrastructure for the InstaBids authentication system and overall application. Our testing strategy includes unit tests, integration tests, security tests, and automated test runners.

## Quick Start

### Backend Testing
```bash
# Navigate to API directory
cd api

# Run all tests with automated runner
python run_tests.py

# Or run specific test types
python -m pytest tests/ -v                    # All tests
python -m pytest tests/ -m unit              # Unit tests only
python -m pytest tests/ -m integration       # Integration tests only
python -m pytest tests/ -m security          # Security tests only
python -m pytest tests/ --cov=.              # With coverage
```

### Frontend Testing
```bash
# Navigate to web directory
cd web

# Run all tests with automated runner
npm run test:all

# Or run specific test types
npm test                                      # All tests
npm run test:watch                           # Watch mode
npm run test:coverage                        # With coverage
npm run test:ci                              # CI mode
```

## Test Architecture

### Backend Test Structure
```
api/tests/
├── conftest.py                              # Test configuration and fixtures
├── test_auth_endpoints.py                   # Authentication API tests (200+ tests)
├── test_supabase_integration.py             # Database integration tests
├── test_integration_auth_flow.py            # End-to-end integration tests
└── test_models.py                           # Data model validation tests
```

### Frontend Test Structure
```
web/src/components/auth/__tests__/
├── RegisterForm.test.tsx                    # Registration form tests
├── LoginForm.test.tsx                       # Login form tests
├── VerifyEmailForm.test.tsx                 # Email verification tests
└── PasswordResetForm.test.tsx               # Password reset tests
```

## Test Categories

### 1. Unit Tests
**Purpose**: Test individual components in isolation

**Backend Examples**:
- API endpoint validation
- Pydantic model validation
- Authentication logic
- Database model methods

**Frontend Examples**:
- React component rendering
- Form validation
- User interactions
- State management

### 2. Integration Tests
**Purpose**: Test complete workflows and system interactions

**Examples**:
- Full registration → verification → login flow
- Database operations with real Supabase
- API endpoint to database integration
- Cross-component communication

### 3. Security Tests
**Purpose**: Validate security measures and prevent vulnerabilities

**Examples**:
- SQL injection prevention
- XSS attack prevention
- Input validation
- Authentication bypass attempts
- Rate limiting validation

### 4. Performance Tests
**Purpose**: Ensure system performs under load

**Examples**:
- API response times
- Database query performance
- Concurrent user handling
- Memory usage validation

## Test Configuration

### Backend Configuration
Located in `api/pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    auth: marks tests related to authentication
    supabase: marks tests that require Supabase connection
    api: marks tests for API endpoints
    security: marks security-related tests
```

### Frontend Configuration
Located in `web/jest.config.js` and `web/package.json`:
```json
{
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/jest.setup.js"],
    "moduleNameMapping": {
      "^@/(.*)$": "<rootDir>/src/$1"
    },
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.d.ts"
    ]
  }
}
```

## Environment Setup

### Required Environment Variables
```bash
# Backend (.env)
SUPABASE_URL=https://lmbpvkfcfhdfaihigfdu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database Requirements
- Active Supabase project (lmbpvkfcfhdfaihigfdu)
- Required tables: users, user_profiles, organizations
- RLS policies configured
- Test data permissions

## Automated Test Runners

### Backend Runner (`api/run_tests.py`)
Features:
- Environment validation
- Sequential test execution
- Comprehensive reporting
- Coverage analysis
- Performance timing
- HTML coverage reports

Usage:
```bash
python run_tests.py
```

### Frontend Runner (`web/scripts/run-tests.js`)
Features:
- Environment validation
- Linting and type checking
- Component testing
- Build validation
- Coverage reporting
- CI/CD compatibility

Usage:
```bash
npm run test:all
```

## Test Data Management

### Test Users
Integration tests create and clean up test users:
```python
# Test user format
{
    "email": "integration-test-{uuid}@instabids.com",
    "password": "TestPass123!",
    "full_name": "Integration Test User",
    "user_type": "property_manager",
    "phone": "+1234567890",
    "organization_name": "Test Organization"
}
```

### Database Cleanup
- Tests use unique UUIDs to avoid conflicts
- Cleanup handled in test teardown
- Isolated test environments

## Coverage Requirements

### Backend Coverage Goals
- **API Endpoints**: 95%+ coverage
- **Authentication Logic**: 100% coverage
- **Database Models**: 90%+ coverage
- **Error Handling**: 85%+ coverage

### Frontend Coverage Goals
- **Components**: 90%+ coverage
- **Forms**: 95%+ coverage
- **Validation**: 100% coverage
- **User Interactions**: 85%+ coverage

## Continuous Integration

### GitHub Actions Integration
```yaml
# Example workflow for backend
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Hook configuration (.pre-commit-config.yaml)
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest tests/ -x
        language: python
        pass_filenames: false
```

## Debugging Tests

### Common Issues

#### Backend Test Failures
```bash
# Check Supabase connection
python -c "from services.supabase import supabase_service; print(supabase_service.client)"

# Check environment variables
python -c "import os; print(os.getenv('SUPABASE_URL'))"

# Run specific test with verbose output
python -m pytest tests/test_auth_endpoints.py::TestUserRegistration::test_register_success -v -s
```

#### Frontend Test Failures
```bash
# Check Jest configuration
npx jest --showConfig

# Run specific test with verbose output
npm test -- --testNamePattern="should render registration form" --verbose

# Debug environment
node -e "console.log(process.env.NEXT_PUBLIC_API_URL)"
```

### Test Debugging Tools
- **Backend**: pytest-pdb, pytest-xvfb
- **Frontend**: Jest debugging, React DevTools
- **Integration**: Network inspection, database queries

## Performance Benchmarks

### Backend Performance Targets
- **Authentication Endpoints**: <500ms response time
- **Database Queries**: <100ms for simple operations
- **Concurrent Users**: 100+ simultaneous requests

### Frontend Performance Targets
- **Component Rendering**: <100ms
- **Form Submission**: <200ms
- **Page Load**: <2s initial load

## Security Testing

### Automated Security Checks
- SQL injection attempts
- XSS payload testing
- Authentication bypass attempts
- Input validation fuzzing
- Rate limiting verification

### Manual Security Testing
- Penetration testing
- Code security review
- Dependency vulnerability scanning
- Authentication flow analysis

## Test Reporting

### Automated Reports
Both test runners generate comprehensive reports:
- **Backend**: `test_report.md`
- **Frontend**: `test-report.md`
- **Coverage**: HTML reports in `htmlcov/` and `coverage/`

### Report Contents
- Test suite summary
- Individual test results
- Coverage percentages
- Performance metrics
- Failure analysis
- Recommendations

## Maintenance

### Regular Tasks
- Update test dependencies monthly
- Review and update test data
- Validate environment configurations
- Update documentation
- Review coverage reports

### Best Practices
1. **Write tests first** (TDD approach)
2. **Keep tests isolated** and independent
3. **Use descriptive test names**
4. **Mock external dependencies**
5. **Maintain high coverage**
6. **Regular test review** and cleanup

## Troubleshooting

### Common Test Failures

#### Environment Issues
```bash
# Fix: Set correct environment variables
export SUPABASE_URL=https://lmbpvkfcfhdfaihigfdu.supabase.co
export SUPABASE_ANON_KEY=your_key_here
```

#### Database Connection Issues
```bash
# Fix: Check Supabase project status
# Verify API keys in Supabase dashboard
# Check network connectivity
```

#### Dependency Issues
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## Getting Help

### Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Supabase Testing Guide](https://supabase.com/docs/guides/getting-started/testing)

### Team Contacts
- Backend Testing: [Your Team]
- Frontend Testing: [Your Team]
- Infrastructure: [Your Team]

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: InstaBids Development Team