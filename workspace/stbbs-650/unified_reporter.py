#!/usr/bin/env python3
"""
Unified Test Reporter
Converts various test formats to the unified reporting format

Usage:
    python unified_reporter.py --input test-results.xml --format junit --output report.json
    python unified_reporter.py --input pytest-results.json --format pytest --output report.json
"""

import json
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class UnifiedReporter:
    """Converts test results to unified reporting format"""
    
    REPORT_VERSION = "1.0"
    
    def __init__(self, environment: str = "dev", test_suite_name: str = "Test Suite"):
        self.environment = environment
        self.test_suite_name = test_suite_name
    
    def create_report_template(self) -> Dict[str, Any]:
        """Create base report structure"""
        return {
            "metadata": {
                "report_id": str(uuid.uuid4()),
                "report_version": self.REPORT_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": {
                    "name": "UnifiedReporter",
                    "version": "1.0.0"
                },
                "environment": {
                    "name": self.environment,
                    "host": Path.cwd().as_posix(),
                    "os": "Python"
                },
                "test_suite": {
                    "name": self.test_suite_name,
                    "version": "1.0.0",
                    "tags": []
                }
            },
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "duration_ms": 0,
                "start_time": "",
                "end_time": "",
                "success_rate": 0.0,
                "status": "PASSED"
            },
            "test_results": [],
            "artifacts": {
                "reports": {}
            }
        }
    
    def convert_junit_xml(self, xml_path: Path) -> Dict[str, Any]:
        """Convert JUnit XML format to unified format"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        report = self.create_report_template()
        
        # Parse summary from testsuites element
        if root.tag == "testsuites":
            report["summary"]["total_tests"] = int(root.get("tests", 0))
            report["summary"]["failed"] = int(root.get("failures", 0))
            report["summary"]["errors"] = int(root.get("errors", 0))
            report["summary"]["skipped"] = int(root.get("skipped", 0))
            report["summary"]["duration_ms"] = int(float(root.get("time", 0)) * 1000)
            
            testsuites = root.findall("testsuite")
        else:
            testsuites = [root]
        
        # Parse individual test cases
        for testsuite in testsuites:
            for testcase in testsuite.findall("testcase"):
                test_result = {
                    "test_id": f"{testcase.get(\'classname\', \'unknown\')}.{testcase.get(\'name\', \'unknown\')}",
                    "test_name": testcase.get("name", "Unknown Test"),
                    "description": "",
                    "status": "PASSED",
                    "duration_ms": int(float(testcase.get("time", 0)) * 1000),
                    "start_time": report["metadata"]["generated_at"],
                    "end_time": report["metadata"]["generated_at"],
                    "assertions": {
                        "total": 1,
                        "passed": 1,
                        "failed": 0
                    },
                    "tags": [],
                    "category": "functional",
                    "severity": "medium",
                    "retry_count": 0,
                    "flaky": False
                }
                
                # Check for failures
                failure = testcase.find("failure")
                if failure is not None:
                    test_result["status"] = "FAILED"
                    test_result["failure_details"] = {
                        "message": failure.get("message", ""),
                        "stack_trace": failure.text or "",
                        "screenshot": "",
                        "logs": ""
                    }
                    test_result["assertions"]["failed"] = 1
                    test_result["assertions"]["passed"] = 0
                
                # Check for errors
                error = testcase.find("error")
                if error is not None:
                    test_result["status"] = "ERROR"
                    test_result["failure_details"] = {
                        "message": error.get("message", ""),
                        "stack_trace": error.text or "",
                        "screenshot": "",
                        "logs": ""
                    }
                
                # Check for skipped
                skipped = testcase.find("skipped")
                if skipped is not None:
                    test_result["status"] = "SKIPPED"
                
                report["test_results"].append(test_result)
        
        # Calculate passed tests
        report["summary"]["passed"] = report["summary"]["total_tests"] - \
                                      report["summary"]["failed"] - \
                                      report["summary"]["errors"] - \
                                      report["summary"]["skipped"]
        
        # Calculate success rate
        if report["summary"]["total_tests"] > 0:
            report["summary"]["success_rate"] = round(
                (report["summary"]["passed"] / report["summary"]["total_tests"]) * 100, 2
            )
        
        # Determine overall status
        if report["summary"]["failed"] > 0 or report["summary"]["errors"] > 0:
            report["summary"]["status"] = "FAILED"
        
        return report
    
    def convert_pytest_json(self, json_path: Path) -> Dict[str, Any]:
        """Convert PyTest JSON format to unified format"""
        with open(json_path, "r") as f:
            pytest_data = json.load(f)
        
        report = self.create_report_template()
        
        # Parse summary
        if "summary" in pytest_data:
            summary = pytest_data["summary"]
            report["summary"]["total_tests"] = summary.get("total", 0)
            report["summary"]["passed"] = summary.get("passed", 0)
            report["summary"]["failed"] = summary.get("failed", 0)
            report["summary"]["skipped"] = summary.get("skipped", 0)
            report["summary"]["errors"] = summary.get("error", 0)
        
        # Parse test results
        for test in pytest_data.get("tests", []):
            outcome = test.get("outcome", "passed")
            status_map = {
                "passed": "PASSED",
                "failed": "FAILED",
                "skipped": "SKIPPED",
                "error": "ERROR"
            }
            
            test_result = {
                "test_id": test.get("nodeid", "unknown"),
                "test_name": test.get("name", "Unknown Test"),
                "description": test.get("doc", ""),
                "status": status_map.get(outcome, "UNKNOWN"),
                "duration_ms": int(test.get("duration", 0) * 1000),
                "start_time": report["metadata"]["generated_at"],
                "end_time": report["metadata"]["generated_at"],
                "assertions": {
                    "total": 1,
                    "passed": 1 if outcome == "passed" else 0,
                    "failed": 1 if outcome == "failed" else 0
                },
                "tags": test.get("markers", []),
                "category": "functional",
                "severity": "medium",
                "retry_count": 0,
                "flaky": False
            }
            
            if outcome == "failed":
                call = test.get("call", {})
                test_result["failure_details"] = {
                    "message": call.get("longrepr", ""),
                    "stack_trace": "",
                    "screenshot": "",
                    "logs": ""
                }
            
            report["test_results"].append(test_result)
        
        # Calculate success rate
        if report["summary"]["total_tests"] > 0:
            report["summary"]["success_rate"] = round(
                (report["summary"]["passed"] / report["summary"]["total_tests"]) * 100, 2
            )
        
        # Determine overall status
        if report["summary"]["failed"] > 0 or report["summary"]["errors"] > 0:
            report["summary"]["status"] = "FAILED"
        
        return report
    
    def validate_report(self, report: Dict[str, Any]) -> List[str]:
        """Validate report against specification"""
        errors = []
        
        # Check required fields
        if "metadata" not in report:
            errors.append("Missing required field: metadata")
        if "summary" not in report:
            errors.append("Missing required field: summary")
        if "test_results" not in report:
            errors.append("Missing required field: test_results")
        
        # Validate counts
        summary = report.get("summary", {})
        total = summary.get("total_tests", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        errors_count = summary.get("errors", 0)
        
        if passed + failed + skipped + errors_count != total:
            errors.append(f"Test count mismatch: {passed}+{failed}+{skipped}+{errors_count} != {total}")
        
        # Validate success rate
        if total > 0:
            expected_rate = round((passed / total) * 100, 2)
            actual_rate = summary.get("success_rate", 0)
            if abs(expected_rate - actual_rate) > 0.01:
                errors.append(f"Success rate mismatch: expected {expected_rate}, got {actual_rate}")
        
        return errors
    
    def save_report(self, report: Dict[str, Any], output_path: Path, format: str = "json"):
        """Save report in specified format"""
        if format == "json":
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report saved: {output_path}")
        else:
            print(f"⚠️  Format {format} not yet implemented")


def main():
    parser = argparse.ArgumentParser(description="Convert test results to unified format")
    parser.add_argument("--input", required=True, help="Input test results file")
    parser.add_argument("--format", required=True, choices=["junit", "pytest"], 
                       help="Input format")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--environment", default="dev", help="Test environment")
    parser.add_argument("--suite-name", default="Test Suite", help="Test suite name")
    
    args = parser.parse_args()
    
    reporter = UnifiedReporter(
        environment=args.environment,
        test_suite_name=args.suite_name
    )
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return 1
    
    print(f"🔄 Converting {args.format} format to unified format...")
    
    if args.format == "junit":
        report = reporter.convert_junit_xml(input_path)
    elif args.format == "pytest":
        report = reporter.convert_pytest_json(input_path)
    else:
        print(f"❌ Unsupported format: {args.format}")
        return 1
    
    print(f"✅ Converted {report[\'summary\'][\'total_tests\']} tests")
    
    # Validate report
    print("🔍 Validating report...")
    errors = reporter.validate_report(report)
    if errors:
        print("⚠️  Validation warnings:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Report validated successfully")
    
    # Save report
    output_path = Path(args.output)
    reporter.save_report(report, output_path)
    
    print(f"\n📊 Summary:")
    print(f"   Total: {report[\'summary\'][\'total_tests\']}")
    print(f"   Passed: {report[\'summary\'][\'passed\']}")
    print(f"   Failed: {report[\'summary\'][\'failed\']}")
    print(f"   Success Rate: {report[\'summary\'][\'success_rate\']}%")
    print(f"   Status: {report[\'summary\'][\'status\']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
