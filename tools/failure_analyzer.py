#!/usr/bin/env python3
"""
Comprehensive Test Failure Analyzer
Extracts and consolidates all failure information from test runs into a compact, actionable format.
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class TestFailureAnalyzer:
    def __init__(self):
        self.failures = []
        self.summary_stats = {
            'total_scenarios': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': 0
        }
        self.assertion_failures = []
        self.error_patterns = []
        
    def analyze_pretty_output(self, pretty_output_file: str) -> Dict[str, Any]:
        """Analyze the pretty.output file and extract all failure information."""
        print(f"Analyzing test results from: {pretty_output_file}")
        
        if not os.path.exists(pretty_output_file):
            print(f"ERROR: File not found: {pretty_output_file}")
            return {}
            
        with open(pretty_output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract summary statistics
        self._extract_summary_stats(content)
        
        # Extract assertion failures
        self._extract_assertion_failures(content)
        
        # Extract failed scenarios
        self._extract_failed_scenarios(content)
        
        # Generate analysis report
        analysis_report = self._generate_analysis_report()
        
        # Save the compact analysis
        self._save_analysis_report(analysis_report)
        
        return analysis_report
    
    def _extract_summary_stats(self, content: str):
        """Extract test execution summary statistics."""
        # Look for summary line pattern: "X features passed, Y failed, Z error, W skipped"
        summary_pattern = r'(\d+)\s+features?\s+passed,\s+(\d+)\s+failed,\s+(\d+)\s+error,\s+(\d+)\s+skipped'
        match = re.search(summary_pattern, content)
        if match:
            self.summary_stats.update({
                'features_passed': int(match.group(1)),
                'features_failed': int(match.group(2)), 
                'features_error': int(match.group(3)),
                'features_skipped': int(match.group(4))
            })
        
        # Look for scenarios summary: "X scenarios passed, Y failed, Z error, W skipped"  
        scenario_pattern = r'(\d+)\s+scenarios?\s+passed,\s+(\d+)\s+failed,\s+(\d+)\s+error,\s+(\d+)\s+skipped'
        match = re.search(scenario_pattern, content)
        if match:
            self.summary_stats.update({
                'scenarios_passed': int(match.group(1)),
                'scenarios_failed': int(match.group(2)),
                'scenarios_error': int(match.group(3)), 
                'scenarios_skipped': int(match.group(4))
            })
        
        # Look for steps summary: "X steps passed, Y failed, Z error, W skipped"
        steps_pattern = r'(\d+)\s+steps?\s+passed,\s+(\d+)\s+failed,\s+(\d+)\s+error,\s+(\d+)\s+skipped'
        match = re.search(steps_pattern, content)
        if match:
            self.summary_stats.update({
                'steps_passed': int(match.group(1)),
                'steps_failed': int(match.group(2)),
                'steps_error': int(match.group(3)),
                'steps_skipped': int(match.group(4))
            })
    
    def _extract_assertion_failures(self, content: str):
        """Extract detailed assertion failure information."""
        # Pattern to match ASSERT FAILED lines
        assert_pattern = r'ASSERT FAILED: (.*?)\. Response: (.*?)(?=\n|$)'
        matches = re.findall(assert_pattern, content, re.DOTALL)
        
        for match in matches:
            assertion_msg = match[0].strip()
            response_data = match[1].strip()
            
            # Try to parse response as JSON for better formatting
            try:
                if response_data.startswith('{') or response_data.startswith('['):
                    response_json = json.loads(response_data)
                    formatted_response = json.dumps(response_json, indent=2)
                else:
                    formatted_response = response_data
            except:
                formatted_response = response_data
                
            self.assertion_failures.append({
                'assertion': assertion_msg,
                'response': formatted_response,
                'type': self._categorize_assertion_failure(assertion_msg)
            })
    
    def _categorize_assertion_failure(self, assertion: str) -> str:
        """Categorize assertion failures by type."""
        if 'Expected status' in assertion:
            return 'HTTP_STATUS_MISMATCH'
        elif 'Content-Length' in assertion:
            return 'CONTENT_LENGTH_ERROR' 
        elif 'JSON' in assertion:
            return 'JSON_PARSING_ERROR'
        elif 'Response is not valid' in assertion:
            return 'INVALID_RESPONSE_FORMAT'
        elif 'IllegalArgumentException' in assertion:
            return 'WIREMOCK_CONFIG_ERROR'
        else:
            return 'GENERAL_ASSERTION_ERROR'
    
    def _extract_failed_scenarios(self, content: str):
        """Extract failed scenario information."""
        # Split content into scenarios
        scenario_pattern = r'@.*?Scenario: (.*?)(?=@.*?Scenario:|$)'
        scenarios = re.findall(scenario_pattern, content, re.DOTALL)
        
        for scenario_content in scenarios:
            if '@FAILED' in scenario_content or 'ASSERT FAILED' in scenario_content:
                scenario_lines = scenario_content.strip().split('\n')
                scenario_name = scenario_lines[0] if scenario_lines else 'Unknown Scenario'
                
                # Extract feature file info
                feature_match = re.search(r'# (features/.*?\.feature:\d+)', scenario_content)
                feature_location = feature_match.group(1) if feature_match else 'Unknown Location'
                
                # Extract tags
                tags_match = re.search(r'@.*?(?=\n|Scenario)', scenario_content)
                tags = tags_match.group(0) if tags_match else ''
                
                # Extract failure reason
                failure_reason = self._extract_failure_reason(scenario_content)
                
                self.failures.append({
                    'scenario': scenario_name.strip(),
                    'location': feature_location,
                    'tags': tags,
                    'failure_reason': failure_reason,
                    'category': self._categorize_failure(failure_reason)
                })
    
    def _extract_failure_reason(self, scenario_content: str) -> str:
        """Extract the specific failure reason from scenario content."""
        if 'ASSERT FAILED' in scenario_content:
            assert_match = re.search(r'ASSERT FAILED: (.*?)(?=\n|$)', scenario_content)
            return assert_match.group(1) if assert_match else 'Assertion failure'
        elif 'ERROR' in scenario_content:
            return 'Test execution error'
        else:
            return 'Unknown failure'
    
    def _categorize_failure(self, failure_reason: str) -> str:
        """Categorize failures for easier grouping and fixing."""
        reason_lower = failure_reason.lower()
        
        if 'content-length' in reason_lower:
            return 'CONTENT_LENGTH_VALIDATION'
        elif 'status' in reason_lower and ('400' in reason_lower or '201' in reason_lower):
            return 'HTTP_STATUS_VALIDATION'
        elif 'json' in reason_lower and 'not valid' in reason_lower:
            return 'RESPONSE_FORMAT_ERROR'
        elif 'conflict' in reason_lower or '409' in reason_lower:
            return 'BUSINESS_LOGIC_ERROR'
        elif 'unauthorized' in reason_lower or '401' in reason_lower:
            return 'AUTHENTICATION_ERROR'
        elif 'enum constant' in reason_lower or 'illegalargumentexception' in reason_lower:
            return 'WIREMOCK_CONFIGURATION_ERROR'
        else:
            return 'GENERAL_ERROR'
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Group failures by category
        failures_by_category = {}
        for failure in self.failures:
            category = failure['category']
            if category not in failures_by_category:
                failures_by_category[category] = []
            failures_by_category[category].append(failure)
        
        # Group assertion failures by type
        assertions_by_type = {}
        for assertion in self.assertion_failures:
            assert_type = assertion['type']
            if assert_type not in assertions_by_type:
                assertions_by_type[assert_type] = []
            assertions_by_type[assert_type].append(assertion)
        
        return {
            'analysis_timestamp': timestamp,
            'summary_statistics': self.summary_stats,
            'total_failures': len(self.failures),
            'total_assertion_failures': len(self.assertion_failures),
            'failures_by_category': failures_by_category,
            'assertion_failures_by_type': assertions_by_type,
            'detailed_failures': self.failures,
            'detailed_assertions': self.assertion_failures,
            'recommended_actions': self._generate_recommendations(failures_by_category)
        }
    
    def _generate_recommendations(self, failures_by_category: Dict[str, List]) -> List[Dict[str, str]]:
        """Generate specific recommendations based on failure patterns."""
        recommendations = []
        
        for category, failures in failures_by_category.items():
            if category == 'CONTENT_LENGTH_VALIDATION':
                recommendations.append({
                    'category': category,
                    'count': len(failures),
                    'action': 'Fix WireMock content-length validation mapping',
                    'file_to_check': '/mnt/c/Users/D/Wiremock/mappings/accounts-mismatched-content-length.json',
                    'specific_issue': 'Content-Length header validation not working properly'
                })
            elif category == 'RESPONSE_FORMAT_ERROR':
                recommendations.append({
                    'category': category, 
                    'count': len(failures),
                    'action': 'Fix WireMock response format for special characters',
                    'file_to_check': '/mnt/c/Users/D/Wiremock/mappings/accounts-get-percent-catch.json',
                    'specific_issue': 'Special character handling returns invalid JSON'
                })
            elif category == 'BUSINESS_LOGIC_ERROR':
                recommendations.append({
                    'category': category,
                    'count': len(failures), 
                    'action': 'Fix booking conflict logic in WireMock',
                    'file_to_check': '/mnt/c/Users/D/Wiremock/mappings/bookings-*.json',
                    'specific_issue': 'Duplicate booking scenarios returning wrong status codes'
                })
            elif category == 'WIREMOCK_CONFIGURATION_ERROR':
                recommendations.append({
                    'category': category,
                    'count': len(failures),
                    'action': 'Fix WireMock DateTimeUnit enum error',
                    'file_to_check': '/mnt/c/Users/D/Wiremock/mappings/loans-*.json', 
                    'specific_issue': 'Invalid DateTimeUnit.MONTH enum causing 500 errors'
                })
        
        return recommendations
    
    def _save_analysis_report(self, report: Dict[str, Any]):
        """Save the analysis report to a file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"test_failure_analysis_{timestamp}.json"
        compact_report_file = f"COMPACT_FAILURE_ANALYSIS_{timestamp}.txt"
        
        # Save detailed JSON report
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save compact text report for easy reading
        self._save_compact_report(report, compact_report_file)
        
        print(f"\nAnalysis complete!")
        print(f"Detailed report: {report_file}")
        print(f"Compact report: {compact_report_file}")
    
    def _save_compact_report(self, report: Dict[str, Any], filename: str):
        """Save a compact, human-readable report."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BANKING API TEST FAILURE ANALYSIS - COMPACT REPORT\n") 
            f.write("=" * 80 + "\n")
            f.write(f"Analysis Timestamp: {report['analysis_timestamp']}\n\n")
            
            # Summary Statistics
            f.write("SUMMARY STATISTICS:\n")
            f.write("-" * 40 + "\n")
            stats = report['summary_statistics']
            if 'scenarios_passed' in stats:
                f.write(f"Scenarios: {stats['scenarios_passed']} passed, {stats['scenarios_failed']} failed, {stats['scenarios_error']} error\n")
            if 'steps_passed' in stats:
                f.write(f"Steps: {stats['steps_passed']} passed, {stats['steps_failed']} failed, {stats['steps_error']} error\n")
            f.write(f"Total Failures: {report['total_failures']}\n")
            f.write(f"Assertion Failures: {report['total_assertion_failures']}\n\n")
            
            # Recommended Actions
            f.write("PRIORITY FIXES NEEDED:\n")
            f.write("-" * 40 + "\n")
            for i, rec in enumerate(report['recommended_actions'], 1):
                f.write(f"{i}. {rec['category']} ({rec['count']} failures)\n")
                f.write(f"   Action: {rec['action']}\n")
                f.write(f"   Check: {rec['file_to_check']}\n")
                f.write(f"   Issue: {rec['specific_issue']}\n\n")
            
            # Assertion Failures by Type
            f.write("ASSERTION FAILURES BY TYPE:\n")
            f.write("-" * 40 + "\n")
            for assert_type, assertions in report['assertion_failures_by_type'].items():
                f.write(f"{assert_type}: {len(assertions)} failures\n")
                for assertion in assertions[:3]:  # Show first 3 examples
                    f.write(f"  - {assertion['assertion']}\n")
                if len(assertions) > 3:
                    f.write(f"  ... and {len(assertions) - 3} more\n")
                f.write("\n")
            
            # Failed Scenarios Summary
            f.write("FAILED SCENARIOS SUMMARY:\n")
            f.write("-" * 40 + "\n")
            for category, failures in report['failures_by_category'].items():
                f.write(f"{category}: {len(failures)} scenarios\n")
                for failure in failures[:2]:  # Show first 2 examples
                    f.write(f"  - {failure['scenario']} ({failure['location']})\n")
                if len(failures) > 2:
                    f.write(f"  ... and {len(failures) - 2} more\n")
                f.write("\n")

def main():
    """Main execution function."""
    analyzer = TestFailureAnalyzer()
    
    # Default pretty.output file location
    pretty_output_file = "/mnt/c/Users/D/python api automation framework/pretty.output"
    
    if len(os.sys.argv) > 1:
        pretty_output_file = os.sys.argv[1]
    
    # Analyze the test results
    analysis_report = analyzer.analyze_pretty_output(pretty_output_file)
    
    if analysis_report:
        print("\n" + "=" * 60)
        print("QUICK SUMMARY:")
        print("=" * 60)
        
        stats = analysis_report['summary_statistics']
        if 'scenarios_failed' in stats:
            print(f"Failed Scenarios: {stats['scenarios_failed']}")
        
        print(f"Total Assertion Failures: {analysis_report['total_assertion_failures']}")
        
        print("\nTOP PRIORITY FIXES:")
        for i, rec in enumerate(analysis_report['recommended_actions'][:3], 1):
            print(f"{i}. {rec['category']} - {rec['specific_issue']}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()