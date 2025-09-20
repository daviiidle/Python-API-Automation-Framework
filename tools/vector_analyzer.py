#!/usr/bin/env python3
"""
Vector-based analysis of pretty.output file for comprehensive test result analysis.
Uses sentence transformers and similarity search to analyze the entire test output.
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Note: These would need to be installed if not available
# pip install sentence-transformers numpy scikit-learn

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    VECTOR_SUPPORT = True
except ImportError:
    print("Vector libraries not available. Using text-based analysis instead.")
    VECTOR_SUPPORT = False


@dataclass
class TestScenario:
    name: str
    feature: str
    status: str
    location: str
    tags: List[str]
    steps: List[str]
    errors: List[str]
    duration: str = ""
    line_start: int = 0
    line_end: int = 0


@dataclass
class TestFailure:
    scenario: str
    error_type: str
    error_message: str
    expected: str
    actual: str
    line_number: int


class VectorTestAnalyzer:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.scenarios: List[TestScenario] = []
        self.failures: List[TestFailure] = []
        self.lines: List[str] = []
        
        if VECTOR_SUPPORT:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings = None
        
    def load_and_parse(self) -> None:
        """Load the entire pretty.output file and parse it comprehensively."""
        print(f"Loading and parsing {self.output_file}...")
        
        with open(self.output_file, 'r', encoding='utf-8', errors='ignore') as f:
            self.lines = f.readlines()
        
        print(f"Loaded {len(self.lines)} lines")
        
        # Parse scenarios and failures
        self._parse_scenarios()
        self._parse_failures()
        
        # Also parse log files for better accuracy
        self._parse_log_files()
        
        print(f"Found {len(self.scenarios)} scenarios and {len(self.failures)} failures")
    
    def _parse_scenarios(self) -> None:
        """Extract all test scenarios from the output."""
        current_scenario = None
        i = 0
        
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # Look for scenario definitions - improved regex
            scenario_match = re.search(r'Scenario:\s*(.+?)(?:\s*#\s*(.+?):\d+)?$', line)
            if scenario_match:
                if current_scenario:
                    current_scenario.line_end = i - 1
                    self.scenarios.append(current_scenario)
                
                scenario_name = scenario_match.group(1).strip()
                location = scenario_match.group(2).strip() if scenario_match.group(2) else "unknown"
                
                # Extract feature name from location
                feature_name = os.path.basename(location).replace('.feature', '').replace('_', ' ').title() if location != "unknown" else "Unknown Feature"
                
                current_scenario = TestScenario(
                    name=scenario_name,
                    feature=feature_name,
                    status="unknown",
                    location=location,
                    tags=[],
                    steps=[],
                    errors=[],
                    line_start=i
                )
                
                # Look for tags in previous lines (expanded search)
                for j in range(max(0, i-10), i):
                    if '@' in self.lines[j]:
                        tags = re.findall(r'@(\w+)', self.lines[j])
                        current_scenario.tags.extend(tags)
            
            # Look for step definitions
            elif current_scenario and (
                line.startswith('Given ') or 
                line.startswith('When ') or 
                line.startswith('Then ') or 
                line.startswith('And ')
            ):
                step_match = re.search(r'(Given|When|Then|And)\s+(.+?)(?:\s*#|$)', line)
                if step_match:
                    current_scenario.steps.append(f"{step_match.group(1)} {step_match.group(2)}")
            
            # Look for errors - improved error detection
            elif current_scenario and ('ASSERT FAILED' in line or 'ERROR' in line or 'FAILED' in line):
                current_scenario.errors.append(line.strip())
                current_scenario.status = "failed"
            
            # Look for success indicators - improved success detection
            elif current_scenario and ('PASSED' in line or 'SUCCESS' in line or 'Status: [PASSED]' in line):
                if current_scenario.status != "failed":
                    current_scenario.status = "passed"
            
            # Look for scenario completion markers from logs
            elif current_scenario and ('SCENARIO COMPLETE' in line):
                if 'PASSED' in line:
                    current_scenario.status = "passed"
                elif 'FAILED' in line:
                    current_scenario.status = "failed"
            
            i += 1
        
        # Don't forget the last scenario
        if current_scenario:
            current_scenario.line_end = len(self.lines) - 1
            self.scenarios.append(current_scenario)
    
    def _parse_log_files(self) -> None:
        """Parse log files to get more accurate scenario status information."""
        log_dir = os.path.dirname(self.output_file)
        log_files = []
        
        # Look for recent log files
        for filename in os.listdir(log_dir):
            if filename.startswith('banking_api_tests_') and filename.endswith('.log'):
                log_files.append(os.path.join(log_dir, filename))
        
        # Get the most recent log file
        if log_files:
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            latest_log = log_files[0]
            
            try:
                with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                    log_lines = f.readlines()
                
                # Update scenario statuses based on log entries
                for line in log_lines:
                    if 'SCENARIO COMPLETE:' in line:
                        if '[PASSED]' in line:
                            scenario_name = line.split('SCENARIO COMPLETE:')[1].split('\n')[0].strip()
                            for scenario in self.scenarios:
                                if scenario.name == scenario_name:
                                    scenario.status = "passed"
                                    break
                        elif '[FAILED]' in line:
                            scenario_name = line.split('SCENARIO COMPLETE:')[1].split('\n')[0].strip()
                            for scenario in self.scenarios:
                                if scenario.name == scenario_name:
                                    scenario.status = "failed"
                                    break
                
                print(f"Updated scenario statuses from log file: {latest_log}")
            except Exception as e:
                print(f"Warning: Could not parse log file {latest_log}: {e}")
    
    def _parse_failures(self) -> None:
        """Extract all failure details from the output."""
        for i, line in enumerate(self.lines):
            if 'ASSERT FAILED' in line:
                # Extract error details
                error_message = line.strip()
                
                # Try to extract expected vs actual
                expected_match = re.search(r'Expected\s+(.+?),\s+got\s+(.+?)\.', error_message)
                if expected_match:
                    expected = expected_match.group(1)
                    actual = expected_match.group(2)
                else:
                    expected = ""
                    actual = ""
                
                # Find which scenario this belongs to
                scenario_name = "Unknown"
                for scenario in self.scenarios:
                    if scenario.line_start <= i <= scenario.line_end:
                        scenario_name = scenario.name
                        break
                
                # Classify error type
                error_type = self._classify_error(error_message)
                
                failure = TestFailure(
                    scenario=scenario_name,
                    error_type=error_type,
                    error_message=error_message,
                    expected=expected,
                    actual=actual,
                    line_number=i
                )
                self.failures.append(failure)
    
    def _classify_error(self, error_message: str) -> str:
        """Classify the type of error."""
        if 'status' in error_message.lower():
            return "Status Code Error"
        elif 'does not contain' in error_message.lower():
            return "Missing Field Error"
        elif 'json' in error_message.lower():
            return "JSON Parsing Error"
        elif 'request was not matched' in error_message.lower():
            return "Endpoint Not Found"
        else:
            return "Other Error"
    
    def create_embeddings(self) -> None:
        """Create vector embeddings for all content if vector support is available."""
        if not VECTOR_SUPPORT:
            print("Vector support not available, skipping embeddings")
            return
        
        print("Creating vector embeddings...")
        
        # Combine all text content
        all_text = []
        for scenario in self.scenarios:
            scenario_text = f"{scenario.name} {scenario.feature} {' '.join(scenario.tags)} {' '.join(scenario.steps)} {' '.join(scenario.errors)}"
            all_text.append(scenario_text)
        
        for failure in self.failures:
            failure_text = f"{failure.scenario} {failure.error_type} {failure.error_message}"
            all_text.append(failure_text)
        
        # Create embeddings
        self.embeddings = self.model.encode(all_text)
        print(f"Created {len(self.embeddings)} embeddings")
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in test results."""
        analysis = {
            "total_scenarios": len(self.scenarios),
            "passed_scenarios": len([s for s in self.scenarios if s.status == "passed"]),
            "failed_scenarios": len([s for s in self.scenarios if s.status == "failed"]),
            "unknown_scenarios": len([s for s in self.scenarios if s.status == "unknown"]),
            "total_failures": len(self.failures),
            "failure_types": defaultdict(int),
            "failing_features": defaultdict(int),
            "common_errors": defaultdict(int),
            "tag_analysis": defaultdict(list)
        }
        
        # Analyze failures
        for failure in self.failures:
            analysis["failure_types"][failure.error_type] += 1
            analysis["common_errors"][failure.error_message[:100]] += 1
        
        # Analyze scenarios by feature and tags
        for scenario in self.scenarios:
            if scenario.status == "failed":
                analysis["failing_features"][scenario.feature] += 1
            
            for tag in scenario.tags:
                analysis["tag_analysis"][tag].append(scenario.status)
        
        # Calculate pass rates by tag
        tag_pass_rates = {}
        for tag, statuses in analysis["tag_analysis"].items():
            total = len(statuses)
            passed = len([s for s in statuses if s == "passed"])
            tag_pass_rates[tag] = round((passed / total * 100), 2) if total > 0 else 0
        
        analysis["tag_pass_rates"] = tag_pass_rates
        analysis["overall_pass_rate"] = round((analysis["passed_scenarios"] / analysis["total_scenarios"] * 100), 2)
        
        return analysis
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar content using vector similarity."""
        if not VECTOR_SUPPORT or self.embeddings is None:
            return []
        
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top k similar items
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.scenarios):
                scenario = self.scenarios[idx]
                results.append((f"Scenario: {scenario.name} ({scenario.status})", similarities[idx]))
            else:
                failure_idx = idx - len(self.scenarios)
                if failure_idx < len(self.failures):
                    failure = self.failures[failure_idx]
                    results.append((f"Failure: {failure.error_type} in {failure.scenario}", similarities[idx]))
        
        return results
    
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report."""
        analysis = self.analyze_patterns()
        
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE TEST ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall summary
        report.append(f"📊 OVERALL RESULTS:")
        report.append(f"   • Total Scenarios: {analysis['total_scenarios']}")
        report.append(f"   • Passed: {analysis['passed_scenarios']} ({analysis['overall_pass_rate']}%)")
        report.append(f"   • Failed: {analysis['failed_scenarios']}")
        report.append(f"   • Unknown: {analysis['unknown_scenarios']}")
        report.append(f"   • Total Failures: {analysis['total_failures']}")
        report.append("")
        
        # Failure type breakdown
        report.append("🚨 FAILURE TYPE BREAKDOWN:")
        for error_type, count in sorted(analysis['failure_types'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"   • {error_type}: {count} occurrences")
        report.append("")
        
        # Failing features
        report.append("📁 FAILING FEATURES:")
        for feature, count in sorted(analysis['failing_features'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"   • {feature}: {count} failures")
        report.append("")
        
        # Tag analysis
        report.append("🏷️  TAG PASS RATES:")
        for tag, pass_rate in sorted(analysis['tag_pass_rates'].items(), key=lambda x: x[1], reverse=True):
            total_scenarios = len(analysis['tag_analysis'][tag])
            report.append(f"   • @{tag}: {pass_rate}% ({total_scenarios} scenarios)")
        report.append("")
        
        # Detailed scenario list
        report.append("📝 SCENARIO DETAILS:")
        for scenario in self.scenarios:
            status_icon = "✅" if scenario.status == "passed" else "❌" if scenario.status == "failed" else "❓"
            report.append(f"   {status_icon} {scenario.name}")
            report.append(f"       Feature: {scenario.feature}")
            report.append(f"       Tags: {', '.join(scenario.tags) if scenario.tags else 'None'}")
            if scenario.errors:
                report.append(f"       Errors: {len(scenario.errors)} errors found")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run the vector analysis."""
    output_file = "/mnt/c/Users/D/python api automation framework/pretty.output"
    
    if not os.path.exists(output_file):
        print(f"Error: {output_file} not found")
        return
    
    # Create analyzer
    analyzer = VectorTestAnalyzer(output_file)
    
    # Load and parse the file
    analyzer.load_and_parse()
    
    # Create embeddings if possible
    analyzer.create_embeddings()
    
    # Generate comprehensive report
    report = analyzer.generate_report()
    
    # Save report
    report_file = "/mnt/c/Users/D/python api automation framework/vector_analysis_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Analysis complete! Report saved to: {report_file}")
    print("\n" + "="*50)
    print("QUICK SUMMARY:")
    print("="*50)
    
    # Print quick summary
    analysis = analyzer.analyze_patterns()
    print(f"Total Scenarios: {analysis['total_scenarios']}")
    print(f"Pass Rate: {analysis['overall_pass_rate']}%")
    print(f"Most Common Failure: {max(analysis['failure_types'].items(), key=lambda x: x[1])[0] if analysis['failure_types'] else 'None'}")
    print(f"Most Problematic Feature: {max(analysis['failing_features'].items(), key=lambda x: x[1])[0] if analysis['failing_features'] else 'None'}")


if __name__ == "__main__":
    main()