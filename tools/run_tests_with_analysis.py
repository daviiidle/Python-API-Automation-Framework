#!/usr/bin/env python3
"""
Test Runner with Automatic Failure Analysis
Runs behave tests and automatically generates comprehensive failure analysis.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_tests_with_analysis():
    """Run behave tests and generate failure analysis."""
    
    print("=" * 80)
    print("BANKING API TESTS WITH AUTOMATIC FAILURE ANALYSIS")
    print("=" * 80)
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Define output files
    pretty_output_file = "pretty.output"
    junit_output_file = f"reports/junit_results_{timestamp}.xml"
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    print(f"Starting test execution at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Pretty output: {pretty_output_file}")
    print(f"JUnit output: {junit_output_file}")
    print("-" * 80)
    
    # Reset WireMock scenarios before running tests
    print("Resetting WireMock scenarios for clean test state...")
    try:
        from reset_wiremock_scenarios import reset_wiremock_scenarios
        if reset_wiremock_scenarios():
            print("✅ WireMock scenarios reset successfully")
        else:
            print("⚠️  Failed to reset WireMock scenarios - tests may have stateful issues")
    except Exception as e:
        print(f"⚠️  Could not reset WireMock scenarios: {e}")
    print("-" * 80)
    
    try:
        # Run behave tests with pretty output and JUnit reporting
        cmd = [
            'behave',
            '--format=pretty',
            f'--outfile={pretty_output_file}',
            '--format=junit',
            f'--outdir=reports',
            '--junit-directory=reports',
            f'--junit-filename=junit_results_{timestamp}.xml',
            '--no-capture',
            '--no-capture-stderr',
            '--show-timings',
            '--verbose'
        ]
        
        # Add any additional arguments passed to this script
        if len(sys.argv) > 1:
            cmd.extend(sys.argv[1:])
        
        print(f"Running command: {' '.join(cmd)}")
        print("-" * 80)
        
        # Execute behave tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        print("-" * 80)
        print(f"Test execution completed with exit code: {result.returncode}")
        print(f"Execution finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1
    
    # Always run failure analysis, regardless of test results
    print("\n" + "=" * 80)
    print("RUNNING AUTOMATIC FAILURE ANALYSIS")
    print("=" * 80)
    
    try:
        # Import and run the failure analyzer
        from failure_analyzer import TestFailureAnalyzer
        
        analyzer = TestFailureAnalyzer()
        analysis_report = analyzer.analyze_pretty_output(pretty_output_file)
        
        if analysis_report and analysis_report['total_failures'] > 0:
            print("\n" + "🔍 FAILURE ANALYSIS COMPLETE")
            print("Check the generated COMPACT_FAILURE_ANALYSIS_*.txt file for actionable insights")
            
            # Show quick summary
            stats = analysis_report['summary_statistics']
            if 'scenarios_failed' in stats and stats['scenarios_failed'] > 0:
                print(f"\n⚠️  {stats['scenarios_failed']} scenarios failed")
                print(f"📋 {analysis_report['total_assertion_failures']} assertion failures detected")
                
                print("\n🎯 TOP PRIORITY FIXES:")
                for i, rec in enumerate(analysis_report['recommended_actions'][:3], 1):
                    print(f"   {i}. {rec['category']}: {rec['specific_issue']}")
                    print(f"      → Check: {rec['file_to_check']}")
            else:
                print("\n✅ All tests passed! No failures to analyze.")
        else:
            print("\n✅ All tests passed! No failures to analyze.")
            
    except Exception as e:
        print(f"Error running failure analysis: {e}")
        print("You can run it manually with: python failure_analyzer.py")
        return 1
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETE")
    print("=" * 80)
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests_with_analysis()
    sys.exit(exit_code)