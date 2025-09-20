#!/usr/bin/env python3
"""
Comprehensive vector-based analyzer for pretty.output file.
Processes the entire file as chunks and provides complete analysis.
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter


@dataclass
class ScenarioResult:
    name: str
    feature: str
    status: str  # passed, failed, skipped, undefined
    location: str
    tags: List[str]
    steps_total: int
    steps_passed: int
    steps_failed: int
    steps_undefined: int
    duration: str
    error_details: List[str]
    api_calls: int
    response_time: float


@dataclass
class FrameworkAnalysis:
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    skipped_scenarios: int
    undefined_scenarios: int
    total_steps: int
    passed_steps: int
    failed_steps: int
    undefined_steps: int
    total_features: int
    error_types: Dict[str, int]
    failing_features: Dict[str, int]
    tag_analysis: Dict[str, Dict[str, int]]
    execution_time: str
    scenarios: List[ScenarioResult]


class ComprehensiveAnalyzer:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.raw_content = ""
        self.analysis = None
    
    def load_entire_file(self) -> str:
        """Load the entire pretty.output file as a single string."""
        print(f"Loading entire file: {self.output_file}")
        
        try:
            with open(self.output_file, 'r', encoding='utf-8', errors='ignore') as f:
                self.raw_content = f.read()
            
            print(f"Successfully loaded {len(self.raw_content):,} characters")
            return self.raw_content
        except Exception as e:
            print(f"Error loading file: {e}")
            return ""
    
    def parse_scenarios_from_content(self) -> List[ScenarioResult]:
        """Parse all scenarios from the raw content using comprehensive regex."""
        scenarios = []
        
        # Split content into scenario blocks
        scenario_blocks = re.split(r'(?=@\w+.*\nFeature:|Scenario:)', self.raw_content)
        
        for block in scenario_blocks:
            if not block.strip() or len(block) < 50:
                continue
            
            scenario = self._parse_single_scenario_block(block)
            if scenario:
                scenarios.append(scenario)
        
        return scenarios
    
    def _parse_single_scenario_block(self, block: str) -> ScenarioResult:
        """Parse a single scenario block comprehensively."""
        lines = block.split('\n')
        
        # Extract scenario name
        scenario_name = "Unknown Scenario"
        feature_name = "Unknown Feature"
        location = "unknown:0"
        tags = []
        
        for line in lines[:20]:  # Check first 20 lines for metadata
            # Find scenario definition
            scenario_match = re.search(r'Scenario:?\s*([^#]+?)(?:\s*#\s*(.+?):\d+)?', line)
            if scenario_match:
                scenario_name = scenario_match.group(1).strip()
                if scenario_match.group(2):
                    location = scenario_match.group(2).strip()
                    feature_name = os.path.basename(location).replace('.feature', '').replace('_', ' ').title()
            
            # Find feature definition
            if 'Feature:' in line and not line.strip().startswith('#'):
                feature_match = re.search(r'Feature:\s*(.+)', line)
                if feature_match:
                    feature_name = feature_match.group(1).strip()
            
            # Extract tags
            if line.strip().startswith('@'):
                tags.extend(re.findall(r'@(\w+)', line))
        
        # Determine status by analyzing the block content
        status = self._determine_scenario_status(block)
        
        # Count steps
        steps_total = len(re.findall(r'^\s*(Given|When|Then|And)\s+', block, re.MULTILINE))
        steps_undefined = len(re.findall(r'#\s*None\s*$', block, re.MULTILINE))
        steps_failed = len(re.findall(r'ASSERT FAILED|ERROR|FAILED', block))
        steps_passed = max(0, steps_total - steps_undefined - steps_failed)
        
        # Extract error details
        error_details = []
        error_matches = re.findall(r'ASSERT FAILED:(.+?)(?:\n|$)', block)
        error_details.extend([err.strip() for err in error_matches])
        
        # Extract performance info
        duration_match = re.search(r'Duration:\s*([0-9:\.]+)', block)
        duration = duration_match.group(1) if duration_match else "0:00:00"
        
        api_calls_match = re.search(r'API Calls Made:\s*(\d+)', block)
        api_calls = int(api_calls_match.group(1)) if api_calls_match else 0
        
        response_time_match = re.search(r'Avg Response Time:\s*([\d\.]+)s', block)
        response_time = float(response_time_match.group(1)) if response_time_match else 0.0
        
        return ScenarioResult(
            name=scenario_name,
            feature=feature_name,
            status=status,
            location=location,
            tags=list(set(tags)),  # Remove duplicates
            steps_total=steps_total,
            steps_passed=steps_passed,
            steps_failed=steps_failed,
            steps_undefined=steps_undefined,
            duration=duration,
            error_details=error_details,
            api_calls=api_calls,
            response_time=response_time
        )
    
    def _determine_scenario_status(self, block: str) -> str:
        """Determine scenario status from block content."""
        # Look for explicit status markers
        if 'Status: [PASSED]' in block or '[PASSED] SCENARIO COMPLETE' in block:
            return "passed"
        elif 'Status: [FAILED]' in block or '[FAILED] SCENARIO COMPLETE' in block:
            return "failed"
        elif 'ASSERT FAILED' in block or 'ERROR' in block:
            return "failed"
        elif '# None' in block:
            return "undefined"
        else:
            return "unknown"
    
    def analyze_comprehensive(self) -> FrameworkAnalysis:
        """Perform comprehensive analysis of all scenarios."""
        # Load content
        content = self.load_entire_file()
        if not content:
            return None
        
        # Parse scenarios
        scenarios = self.parse_scenarios_from_content()
        
        if not scenarios:
            print("Warning: No scenarios found in analysis")
            return None
        
        # Calculate statistics
        total_scenarios = len(scenarios)
        passed_scenarios = len([s for s in scenarios if s.status == "passed"])
        failed_scenarios = len([s for s in scenarios if s.status == "failed"])
        skipped_scenarios = len([s for s in scenarios if s.status == "skipped"])
        undefined_scenarios = len([s for s in scenarios if s.status == "undefined"])
        
        # Step statistics
        total_steps = sum(s.steps_total for s in scenarios)
        passed_steps = sum(s.steps_passed for s in scenarios)
        failed_steps = sum(s.steps_failed for s in scenarios)
        undefined_steps = sum(s.steps_undefined for s in scenarios)
        
        # Feature analysis
        features = set(s.feature for s in scenarios)
        total_features = len(features)
        
        # Error type analysis
        error_types = Counter()
        for scenario in scenarios:
            for error in scenario.error_details:
                if 'status' in error.lower():
                    error_types['Status Code Error'] += 1
                elif 'does not contain' in error.lower():
                    error_types['Missing Field Error'] += 1
                elif 'json' in error.lower():
                    error_types['JSON Error'] += 1
                elif 'timeout' in error.lower():
                    error_types['Timeout Error'] += 1
                else:
                    error_types['Other Error'] += 1
        
        # Failing features analysis
        failing_features = Counter()
        for scenario in scenarios:
            if scenario.status == "failed":
                failing_features[scenario.feature] += 1
        
        # Tag analysis
        tag_analysis = defaultdict(lambda: {'passed': 0, 'failed': 0, 'undefined': 0, 'total': 0})
        for scenario in scenarios:
            for tag in scenario.tags:
                tag_analysis[tag]['total'] += 1
                if scenario.status in tag_analysis[tag]:
                    tag_analysis[tag][scenario.status] += 1
        
        # Extract execution time
        execution_time_match = re.search(r'Took\s+([\d\w\s\.]+)', content)
        execution_time = execution_time_match.group(1) if execution_time_match else "Unknown"
        
        self.analysis = FrameworkAnalysis(
            total_scenarios=total_scenarios,
            passed_scenarios=passed_scenarios,
            failed_scenarios=failed_scenarios,
            skipped_scenarios=skipped_scenarios,
            undefined_scenarios=undefined_scenarios,
            total_steps=total_steps,
            passed_steps=passed_steps,
            failed_steps=failed_steps,
            undefined_steps=undefined_steps,
            total_features=total_features,
            error_types=dict(error_types),
            failing_features=dict(failing_features),
            tag_analysis=dict(tag_analysis),
            execution_time=execution_time,
            scenarios=scenarios
        )
        
        return self.analysis
    
    def generate_detailed_report(self) -> str:
        """Generate a comprehensive detailed report."""
        if not self.analysis:
            return "No analysis available. Run analyze_comprehensive() first."
        
        report = []
        report.append("=" * 100)
        report.append("COMPREHENSIVE BANKING API BDD FRAMEWORK ANALYSIS")
        report.append("=" * 100)
        report.append("")
        
        # Executive summary
        pass_rate = (self.analysis.passed_scenarios / self.analysis.total_scenarios * 100) if self.analysis.total_scenarios > 0 else 0
        report.append(f"🎯 EXECUTIVE SUMMARY:")
        report.append(f"   Total Scenarios: {self.analysis.total_scenarios}")
        report.append(f"   Pass Rate: {pass_rate:.1f}%")
        report.append(f"   Execution Time: {self.analysis.execution_time}")
        report.append("")
        
        # Detailed results
        report.append(f"📊 DETAILED RESULTS:")
        report.append(f"   ✅ Passed:     {self.analysis.passed_scenarios:3d} scenarios ({self.analysis.passed_scenarios/self.analysis.total_scenarios*100:5.1f}%)")
        report.append(f"   ❌ Failed:     {self.analysis.failed_scenarios:3d} scenarios ({self.analysis.failed_scenarios/self.analysis.total_scenarios*100:5.1f}%)")
        report.append(f"   ❓ Undefined:  {self.analysis.undefined_scenarios:3d} scenarios ({self.analysis.undefined_scenarios/self.analysis.total_scenarios*100:5.1f}%)")
        report.append(f"   ⏭️  Skipped:    {self.analysis.skipped_scenarios:3d} scenarios ({self.analysis.skipped_scenarios/self.analysis.total_scenarios*100:5.1f}%)")
        report.append("")
        
        # Step analysis
        report.append(f"📋 STEP ANALYSIS:")
        report.append(f"   Total Steps:     {self.analysis.total_steps}")
        report.append(f"   Passed Steps:    {self.analysis.passed_steps}")
        report.append(f"   Failed Steps:    {self.analysis.failed_steps}")
        report.append(f"   Undefined Steps: {self.analysis.undefined_steps}")
        report.append("")
        
        # Error analysis
        if self.analysis.error_types:
            report.append(f"🚨 ERROR TYPE BREAKDOWN:")
            for error_type, count in sorted(self.analysis.error_types.items(), key=lambda x: x[1], reverse=True):
                report.append(f"   • {error_type}: {count} occurrences")
            report.append("")
        
        # Feature analysis
        if self.analysis.failing_features:
            report.append(f"📁 MOST PROBLEMATIC FEATURES:")
            for feature, count in sorted(self.analysis.failing_features.items(), key=lambda x: x[1], reverse=True):
                report.append(f"   • {feature}: {count} failures")
            report.append("")
        
        # Tag analysis - top failing tags
        report.append(f"🏷️  TAG PASS RATES (Showing tags with >2 scenarios):")
        tag_rates = []
        for tag, stats in self.analysis.tag_analysis.items():
            if stats['total'] >= 2:
                pass_rate = (stats.get('passed', 0) / stats['total'] * 100) if stats['total'] > 0 else 0
                tag_rates.append((tag, pass_rate, stats['total'], stats.get('failed', 0)))
        
        # Sort by pass rate (ascending) to show most problematic tags first
        for tag, pass_rate, total, failed in sorted(tag_rates, key=lambda x: x[1]):
            report.append(f"   @{tag:20s}: {pass_rate:5.1f}% ({total} scenarios, {failed} failed)")
        report.append("")
        
        # Detailed scenario breakdown
        report.append(f"📝 DETAILED SCENARIO BREAKDOWN:")
        report.append("")
        
        current_feature = ""
        for scenario in sorted(self.analysis.scenarios, key=lambda x: (x.feature, x.status, x.name)):
            if scenario.feature != current_feature:
                current_feature = scenario.feature
                report.append(f"🗂️  FEATURE: {current_feature}")
                report.append("-" * 60)
            
            status_icon = {"passed": "✅", "failed": "❌", "undefined": "❓", "skipped": "⏭️", "unknown": "❓"}.get(scenario.status, "❓")
            
            report.append(f"   {status_icon} {scenario.name}")
            if scenario.tags:
                report.append(f"       Tags: {', '.join(scenario.tags[:5])}")  # Limit to first 5 tags
            
            if scenario.steps_total > 0:
                report.append(f"       Steps: {scenario.steps_total} total, {scenario.steps_passed} passed, {scenario.steps_failed} failed, {scenario.steps_undefined} undefined")
            
            if scenario.error_details:
                report.append(f"       Errors: {len(scenario.error_details)} error(s)")
                for error in scenario.error_details[:2]:  # Show first 2 errors
                    report.append(f"         • {error[:100]}{'...' if len(error) > 100 else ''}")
            
            if scenario.api_calls > 0:
                report.append(f"       Performance: {scenario.api_calls} API calls, {scenario.response_time:.3f}s avg response time")
            
            report.append("")
        
        # Recommendations
        report.append("🎯 PRIORITY RECOMMENDATIONS:")
        report.append("")
        
        if self.analysis.undefined_steps > 0:
            report.append(f"1. 🔧 IMPLEMENT UNDEFINED STEPS: {self.analysis.undefined_steps} steps need implementation")
            report.append(f"   This affects {self.analysis.undefined_scenarios} scenarios and is blocking progress")
        
        if self.analysis.failing_features:
            top_failing = max(self.analysis.failing_features.items(), key=lambda x: x[1])
            report.append(f"2. 🚨 FIX TOP FAILING FEATURE: '{top_failing[0]}' has {top_failing[1]} failures")
        
        if self.analysis.error_types:
            top_error = max(self.analysis.error_types.items(), key=lambda x: x[1])
            report.append(f"3. 🔍 ADDRESS TOP ERROR TYPE: '{top_error[0]}' causes {top_error[1]} failures")
        
        report.append("")
        report.append("=" * 100)
        
        return "\n".join(report)
    
    def save_report(self, report_path: str = None) -> str:
        """Save the comprehensive report to file."""
        if not report_path:
            report_path = "comprehensive_analysis_report.txt"
        
        report = self.generate_detailed_report()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_path


def main():
    """Main function to run comprehensive analysis."""
    output_file = "/mnt/c/Users/D/python api automation framework/pretty.output"
    
    if not os.path.exists(output_file):
        print(f"Error: {output_file} not found")
        return
    
    # Create analyzer
    analyzer = ComprehensiveAnalyzer(output_file)
    
    # Run comprehensive analysis
    print("Starting comprehensive analysis...")
    analysis = analyzer.analyze_comprehensive()
    
    if not analysis:
        print("Failed to analyze file")
        return
    
    # Generate and save report
    report_path = analyzer.save_report("/mnt/c/Users/D/python api automation framework/comprehensive_analysis_report.txt")
    
    # Print summary
    print("\n" + "="*80)
    print("COMPREHENSIVE ANALYSIS COMPLETE")
    print("="*80)
    
    pass_rate = (analysis.passed_scenarios / analysis.total_scenarios * 100) if analysis.total_scenarios > 0 else 0
    
    print(f"📊 RESULTS: {analysis.passed_scenarios}/{analysis.total_scenarios} scenarios passed ({pass_rate:.1f}%)")
    print(f"📋 STEPS: {analysis.passed_steps}/{analysis.total_steps} steps working")
    print(f"🚨 TOP ERROR: {max(analysis.error_types.items(), key=lambda x: x[1])[0] if analysis.error_types else 'None'}")
    print(f"📁 WORST FEATURE: {max(analysis.failing_features.items(), key=lambda x: x[1])[0] if analysis.failing_features else 'None'}")
    print(f"📄 REPORT: {report_path}")
    print("="*80)


if __name__ == "__main__":
    main()