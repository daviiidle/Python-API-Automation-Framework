#!/usr/bin/env python3
"""
Failure Summary Generator for Banking API BDD Tests

This script parses JUnit XML test results and generates a concise failure summary
for easy debugging and analysis.
"""

import os
import sys
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
import re


class TestFailure:
    """Represents a single test failure with relevant details."""

    def __init__(self, name: str, classname: str, message: str, failure_type: str, time: float):
        self.name = name
        self.classname = classname
        self.message = message
        self.failure_type = failure_type
        self.time = time
        self.category = self._categorize_failure()

    def _categorize_failure(self) -> str:
        """Categorize failure based on error message."""
        message_lower = self.message.lower()

        if 'timeout' in message_lower or 'timed out' in message_lower:
            return '⏱️ Timeout'
        elif 'assertion' in message_lower or 'expected' in message_lower:
            return '❌ Assertion'
        elif 'connection' in message_lower or 'network' in message_lower:
            return '🌐 Network'
        elif 'authentication' in message_lower or 'auth' in message_lower:
            return '🔐 Authentication'
        elif '401' in message_lower or '403' in message_lower:
            return '🚫 Authorization'
        elif '404' in message_lower:
            return '🔍 Not Found'
        elif '500' in message_lower or '502' in message_lower or '503' in message_lower:
            return '🚨 Server Error'
        elif 'json' in message_lower or 'parse' in message_lower:
            return '📄 Data Format'
        else:
            return '❓ Other'


class FailureSummaryGenerator:
    """Generates failure summary from JUnit XML reports."""

    def __init__(self, reports_dir: str = "reports/junit"):
        self.reports_dir = reports_dir
        self.failures: List[TestFailure] = []
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_skipped = 0

    def parse_junit_reports(self):
        """Parse all JUnit XML files in the reports directory."""
        xml_files = glob.glob(os.path.join(self.reports_dir, "*.xml"))

        if not xml_files:
            print(f"No JUnit XML files found in {self.reports_dir}")
            return

        for xml_file in xml_files:
            self._parse_xml_file(xml_file)

    def _parse_xml_file(self, xml_file: str):
        """Parse a single JUnit XML file."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Handle different XML structures
            if root.tag == 'testsuites':
                testsuites = root.findall('testsuite')
            elif root.tag == 'testsuite':
                testsuites = [root]
            else:
                print(f"Unknown XML structure in {xml_file}")
                return

            for testsuite in testsuites:
                self._parse_testsuite(testsuite, xml_file)

        except ET.ParseError as e:
            print(f"Error parsing {xml_file}: {e}")
        except Exception as e:
            print(f"Unexpected error parsing {xml_file}: {e}")

    def _parse_testsuite(self, testsuite: ET.Element, source_file: str):
        """Parse a single test suite element."""
        # Update statistics
        self.total_tests += int(testsuite.get('tests', 0))
        self.total_failures += int(testsuite.get('failures', 0))
        self.total_errors += int(testsuite.get('errors', 0))
        self.total_skipped += int(testsuite.get('skipped', 0))

        # Process test cases
        for testcase in testsuite.findall('testcase'):
            self._process_testcase(testcase, source_file)

    def _process_testcase(self, testcase: ET.Element, source_file: str):
        """Process a single test case element."""
        name = testcase.get('name', 'Unknown Test')
        classname = testcase.get('classname', 'Unknown Class')
        time = float(testcase.get('time', 0))

        # Check for failures
        failure = testcase.find('failure')
        error = testcase.find('error')

        if failure is not None:
            message = failure.get('message', failure.text or 'No failure message')
            failure_type = failure.get('type', 'Unknown')
            self.failures.append(TestFailure(name, classname, message, failure_type, time))

        elif error is not None:
            message = error.get('message', error.text or 'No error message')
            error_type = error.get('type', 'Unknown')
            self.failures.append(TestFailure(name, classname, message, error_type, time))

    def generate_summary(self, output_file: str = "failure_summary.md"):
        """Generate the failure summary markdown report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            self._write_header(f)
            self._write_overview(f)

            if self.failures:
                self._write_failure_details(f)
                self._write_failure_categories(f)
                self._write_recommendations(f)
            else:
                f.write("## 🎉 All Tests Passed!\n\n")
                f.write("No failures detected in the test run.\n\n")

            self._write_footer(f)

        print(f"Failure summary generated: {output_file}")

    def _write_header(self, f):
        """Write the report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        f.write(f"# 🚨 Test Failure Summary\n\n")
        f.write(f"**Generated:** {timestamp}  \n")
        f.write(f"**Reports Directory:** `{self.reports_dir}`\n\n")
        f.write("---\n\n")

    def _write_overview(self, f):
        """Write the test overview section."""
        pass_rate = ((self.total_tests - self.total_failures - self.total_errors) / max(self.total_tests, 1)) * 100

        f.write("## 📊 Test Execution Overview\n\n")
        f.write(f"| Metric | Count | Percentage |\n")
        f.write(f"|--------|--------|------------|\n")
        f.write(f"| **Total Tests** | {self.total_tests} | 100% |\n")
        f.write(f"| **Passed** | {self.total_tests - self.total_failures - self.total_errors} | {pass_rate:.1f}% |\n")
        f.write(f"| **Failed** | {self.total_failures} | {(self.total_failures/max(self.total_tests,1)*100):.1f}% |\n")
        f.write(f"| **Errors** | {self.total_errors} | {(self.total_errors/max(self.total_tests,1)*100):.1f}% |\n")
        f.write(f"| **Skipped** | {self.total_skipped} | {(self.total_skipped/max(self.total_tests,1)*100):.1f}% |\n\n")

    def _write_failure_details(self, f):
        """Write detailed failure information."""
        f.write("## 🔍 Failed Test Details\n\n")

        for i, failure in enumerate(self.failures, 1):
            f.write(f"### {i}. {failure.name}\n\n")
            f.write(f"- **Category:** {failure.category}\n")
            f.write(f"- **Class:** `{failure.classname}`\n")
            f.write(f"- **Duration:** {failure.time:.2f}s\n")
            f.write(f"- **Type:** `{failure.failure_type}`\n\n")

            # Clean and format error message
            clean_message = self._clean_error_message(failure.message)
            f.write(f"**Error Message:**\n```\n{clean_message}\n```\n\n")

            # Extract feature file location if possible
            feature_location = self._extract_feature_location(failure.classname)
            if feature_location:
                f.write(f"**Likely Location:** `{feature_location}`\n\n")

            f.write("---\n\n")

    def _write_failure_categories(self, f):
        """Write failure categories summary."""
        if not self.failures:
            return

        f.write("## 📋 Failure Categories\n\n")

        # Count failures by category
        categories = {}
        for failure in self.failures:
            categories[failure.category] = categories.get(failure.category, 0) + 1

        # Sort by count (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

        f.write("| Category | Count | Tests |\n")
        f.write("|----------|-------|-------|\n")

        for category, count in sorted_categories:
            test_names = [f.name for f in self.failures if f.category == category]
            test_list = ", ".join(test_names[:3])  # Show first 3 tests
            if len(test_names) > 3:
                test_list += f", ... (+{len(test_names)-3} more)"

            f.write(f"| {category} | {count} | {test_list} |\n")

        f.write("\n")

    def _write_recommendations(self, f):
        """Write recommendations based on failure patterns."""
        if not self.failures:
            return

        f.write("## 💡 Recommended Actions\n\n")

        # Count categories for recommendations
        categories = [failure.category for failure in self.failures]

        if any('Timeout' in cat for cat in categories):
            f.write("- **⏱️ Timeout Issues:** Consider increasing timeout values or improving API response times\n")

        if any('Assertion' in cat for cat in categories):
            f.write("- **❌ Assertion Failures:** Review test expectations and API response formats\n")

        if any('Network' in cat for cat in categories):
            f.write("- **🌐 Network Issues:** Check API connectivity and network stability\n")

        if any('Authentication' in cat for cat in categories):
            f.write("- **🔐 Authentication Problems:** Verify API credentials and token validity\n")

        if any('Server Error' in cat for cat in categories):
            f.write("- **🚨 Server Errors:** Check API server health and error logs\n")

        f.write("\n")

    def _write_footer(self, f):
        """Write the report footer."""
        f.write("---\n\n")
        f.write("*Generated by Banking API BDD Test Framework*\n")
        f.write(f"*Total Analysis Time: {len(self.failures)} failures processed*\n")

    def _clean_error_message(self, message: str) -> str:
        """Clean and format error message for better readability."""
        if not message:
            return "No error message available"

        # Remove excessive whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', message.strip())

        # Truncate very long messages
        if len(cleaned) > 500:
            cleaned = cleaned[:500] + "... (truncated)"

        return cleaned

    def _extract_feature_location(self, classname: str) -> str:
        """Extract likely feature file location from classname."""
        if not classname:
            return ""

        # Convert classname to feature file path
        # e.g., "accounts.account_creation.Account Creation" -> "features/accounts/account_creation.feature"
        parts = classname.split('.')
        if len(parts) >= 2:
            return f"features/{parts[0]}/{parts[1]}.feature"
        elif len(parts) == 1:
            return f"features/{parts[0]}/*.feature"

        return ""


def main():
    """Main function to generate failure summary."""
    # Default reports directory
    reports_dir = "reports/junit"

    # Allow custom reports directory from command line
    if len(sys.argv) > 1:
        reports_dir = sys.argv[1]

    # Check if reports directory exists
    if not os.path.exists(reports_dir):
        print(f"Reports directory not found: {reports_dir}")
        print("Creating empty failure summary...")

        # Create empty summary
        with open("failure_summary.md", 'w') as f:
            f.write("# 🚨 Test Failure Summary\n\n")
            f.write("**No test reports found**\n\n")
            f.write(f"Reports directory `{reports_dir}` does not exist.\n")
        return

    # Generate failure summary
    generator = FailureSummaryGenerator(reports_dir)
    generator.parse_junit_reports()
    generator.generate_summary()

    # Print summary to console
    print(f"\n📊 Summary Generated:")
    print(f"   Total Tests: {generator.total_tests}")
    print(f"   Failed: {generator.total_failures + generator.total_errors}")
    print(f"   Pass Rate: {((generator.total_tests - generator.total_failures - generator.total_errors) / max(generator.total_tests, 1)) * 100:.1f}%")


if __name__ == "__main__":
    main()