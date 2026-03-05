# Unified Reporting Format Specification

## Overview
This document defines the standard format for all solution test reports to ensure consistency, ease of parsing, and integration across different testing frameworks and environments.

**Version:** 1.0  
**Status:** Draft  
**Last Updated:** 2026-03-05

## Objectives
1. Standardize report format across all test solutions
2. Enable automated parsing and aggregation
3. Support multiple output formats (JSON, XML, HTML)
4. Facilitate integration with CI/CD pipelines
5. Provide clear audit trail and traceability

---

## Report Structure

### 1. Metadata Section
Every report MUST include the following metadata:

```json
{
  "metadata": {
    "report_id": "UUID",
    "report_version": "1.0",
    "generated_at": "ISO-8601 timestamp",
    "generator": {
      "name": "Test framework name",
      "version": "Framework version"
    },
    "environment": {
      "name": "dev|staging|prod",
      "host": "hostname",
      "os": "Operating system"
    },
    "test_suite": {
      "name": "Test suite name",
      "version": "Test version",
      "tags": ["tag1", "tag2"]
    }
  }
}
```

**Field Descriptions:**
- `report_id`: Unique UUID for this report instance
- `generated_at`: ISO-8601 timestamp (e.g., "2026-03-05T10:30:00Z")
- `environment.name`: Target environment where tests ran
- `test_suite.tags`: Categorization tags (e.g., ["smoke", "regression"])

---

### 2. Execution Summary
High-level summary of test execution:

```json
{
  "summary": {
    "total_tests": 150,
    "passed": 145,
    "failed": 3,
    "skipped": 2,
    "errors": 0,
    "duration_ms": 45000,
    "start_time": "ISO-8601 timestamp",
    "end_time": "ISO-8601 timestamp",
    "success_rate": 96.67,
    "status": "PASSED|FAILED|ERROR"
  }
}
```

**Calculation Rules:**
- `success_rate` = (passed / total_tests) × 100
- `status` = "PASSED" if failed == 0 and errors == 0, else "FAILED"
- `duration_ms` = Total execution time in milliseconds

---

### 3. Test Results
Detailed results for each test case:

```json
{
  "test_results": [
    {
      "test_id": "test_login_valid_credentials",
      "test_name": "Verify login with valid credentials",
      "description": "Tests successful login flow",
      "status": "PASSED|FAILED|SKIPPED|ERROR",
      "duration_ms": 1250,
      "start_time": "ISO-8601 timestamp",
      "end_time": "ISO-8601 timestamp",
      "assertions": {
        "total": 5,
        "passed": 5,
        "failed": 0
      },
      "tags": ["authentication", "smoke"],
      "category": "functional",
      "severity": "critical|high|medium|low",
      "failure_details": {
        "message": "Error message if failed",
        "stack_trace": "Full stack trace",
        "screenshot": "path/to/screenshot.png",
        "logs": "Relevant log excerpts"
      },
      "retry_count": 0,
      "flaky": false
    }
  ]
}
```

**Status Values:**
- `PASSED`: Test completed successfully
- `FAILED`: Test failed with assertion error
- `SKIPPED`: Test was intentionally skipped
- `ERROR`: Test encountered an error (not assertion failure)

**Severity Levels:**
- `critical`: Must pass for release
- `high`: Important functionality
- `medium`: Standard functionality
- `low`: Nice-to-have features

---

### 4. Coverage Information
Code coverage metrics (if applicable):

```json
{
  "coverage": {
    "line_coverage": 85.5,
    "branch_coverage": 78.3,
    "function_coverage": 92.1,
    "statement_coverage": 84.7,
    "covered_lines": 8550,
    "total_lines": 10000,
    "report_path": "coverage/index.html"
  }
}
```

---

### 5. Performance Metrics
Performance-related measurements:

```json
{
  "performance": {
    "average_response_time_ms": 250,
    "max_response_time_ms": 1500,
    "min_response_time_ms": 50,
    "p95_response_time_ms": 800,
    "p99_response_time_ms": 1200,
    "throughput_requests_per_sec": 100,
    "error_rate_percent": 0.5
  }
}
```

---

### 6. Artifacts
Links to generated artifacts:

```json
{
  "artifacts": {
    "screenshots": ["url1", "url2"],
    "videos": ["url1"],
    "logs": ["url1", "url2"],
    "reports": {
      "html": "path/to/report.html",
      "json": "path/to/report.json",
      "xml": "path/to/report.xml"
    }
  }
}
```

---

### 7. Integration Data
CI/CD and version control information:

```json
{
  "integration": {
    "ci_system": "Jenkins|GitLab|GitHub Actions",
    "build_id": "12345",
    "build_url": "https://ci.example.com/build/12345",
    "commit": {
      "sha": "abc123def456",
      "branch": "main",
      "author": "john.doe@example.com",
      "message": "Fix login bug",
      "timestamp": "ISO-8601 timestamp"
    },
    "pull_request": {
      "number": 123,
      "url": "https://github.com/org/repo/pull/123"
    }
  }
}
```

---

## Complete Example Report

```json
{
  "metadata": {
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "report_version": "1.0",
    "generated_at": "2026-03-05T10:30:00Z",
    "generator": {
      "name": "PyTest",
      "version": "7.4.0"
    },
    "environment": {
      "name": "staging",
      "host": "test-runner-01",
      "os": "Ubuntu 22.04"
    },
    "test_suite": {
      "name": "Vertex Solution Tests",
      "version": "2.0.0",
      "tags": ["regression", "api"]
    }
  },
  "summary": {
    "total_tests": 150,
    "passed": 145,
    "failed": 3,
    "skipped": 2,
    "errors": 0,
    "duration_ms": 45000,
    "start_time": "2026-03-05T10:30:00Z",
    "end_time": "2026-03-05T10:30:45Z",
    "success_rate": 96.67,
    "status": "FAILED"
  },
  "test_results": [
    {
      "test_id": "test_login_valid",
      "test_name": "Verify login with valid credentials",
      "description": "Tests successful login flow with valid user credentials",
      "status": "PASSED",
      "duration_ms": 1250,
      "start_time": "2026-03-05T10:30:00Z",
      "end_time": "2026-03-05T10:30:01.250Z",
      "assertions": {
        "total": 5,
        "passed": 5,
        "failed": 0
      },
      "tags": ["authentication", "smoke"],
      "category": "functional",
      "severity": "critical",
      "retry_count": 0,
      "flaky": false
    }
  ],
  "coverage": {
    "line_coverage": 85.5,
    "branch_coverage": 78.3,
    "function_coverage": 92.1,
    "covered_lines": 8550,
    "total_lines": 10000,
    "report_path": "coverage/index.html"
  },
  "performance": {
    "average_response_time_ms": 250,
    "p95_response_time_ms": 800,
    "p99_response_time_ms": 1200
  },
  "artifacts": {
    "reports": {
      "html": "reports/test-report.html",
      "json": "reports/test-report.json"
    }
  },
  "integration": {
    "ci_system": "GitLab CI",
    "build_id": "12345",
    "build_url": "https://gitlab.com/vertex/project/-/jobs/12345",
    "commit": {
      "sha": "abc123def456",
      "branch": "main",
      "author": "developer@vertex.com",
      "message": "Add new test cases",
      "timestamp": "2026-03-05T09:00:00Z"
    }
  }
}
```

---

## Field Mapping Guide

### From JUnit XML to Unified Format
| JUnit XML | Unified Format |
|-----------|----------------|
| `testsuites/@tests` | `summary.total_tests` |
| `testsuites/@failures` | `summary.failed` |
| `testsuites/@time` | `summary.duration_ms` (convert to ms) |
| `testcase/@name` | `test_results[].test_name` |
| `testcase/@time` | `test_results[].duration_ms` |
| `testcase/failure` | `test_results[].status = "FAILED"` |

### From PyTest JSON to Unified Format
| PyTest JSON | Unified Format |
|-------------|----------------|
| `summary.total` | `summary.total_tests` |
| `summary.passed` | `summary.passed` |
| `summary.failed` | `summary.failed` |
| `tests[].nodeid` | `test_results[].test_id` |
| `tests[].outcome` | `test_results[].status` (map values) |
| `tests[].duration` | `test_results[].duration_ms` (convert to ms) |

---

## Data Types

| Field | Type | Format | Required |
|-------|------|--------|----------|
| `report_id` | String | UUID v4 | Yes |
| `generated_at` | String | ISO-8601 | Yes |
| `total_tests` | Integer | >= 0 | Yes |
| `duration_ms` | Integer | >= 0 | Yes |
| `success_rate` | Float | 0-100 with 2 decimals | Yes |
| `status` | Enum | PASSED\|FAILED\|ERROR | Yes |
| `tags` | Array | String[] | No |
| `severity` | Enum | critical\|high\|medium\|low | No |

---

## Validation Rules

1. **Required Fields**: All fields marked "Required: Yes" must be present
2. **Status Logic**: If any test has status "FAILED", summary.status must be "FAILED"
3. **Time Consistency**: `end_time` must be >= `start_time`
4. **Count Consistency**: `total_tests` = `passed` + `failed` + `skipped` + `errors`
5. **Success Rate**: Must match calculated value within 0.01%
6. **UUID Format**: All IDs must be valid UUID v4 format

---

## Output Formats

### JSON (Primary)
- Default and recommended format
- File extension: `.json`
- MIME type: `application/json`
- UTF-8 encoding

### XML (Legacy Support)
- For compatibility with older systems
- File extension: `.xml`
- Root element: `<test_report>`

### HTML (Human-Readable)
- For viewing in browsers
- File extension: `.html`
- Must include CSS for styling

---

## Implementation Checklist

- [ ] Report generator validates all required fields
- [ ] Timestamps use ISO-8601 format with timezone
- [ ] File names include timestamp: `test-report-20260305-103000.json`
- [ ] Reports stored in designated directory structure
- [ ] Validation against JSON schema before publishing
- [ ] Automated tests for report generation
- [ ] Documentation for consumers
- [ ] CI/CD integration examples

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-05 | Initial specification |

---

**Generated by AI DevOps Agent**  
**For Jira Ticket:** STBBS-650  
**Status:** Ready for Review
