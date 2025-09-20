#!/usr/bin/env python3
"""
Parallel test execution script for Banking API BDD Framework.
Enables running Behave tests in parallel using multiple processes.
"""

import os
import sys
import subprocess
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from datetime import datetime


def run_tag_group(tag_group, output_dir):
    """Run a specific tag group in a separate process."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'output_{tag_group.replace("@", "")}_{timestamp}.txt')
    
    cmd = [
        sys.executable, '-m', 'behave',
        '--tags', tag_group,
        '--format', 'pretty',
        '--no-capture',
        '--junit',
        '--junit-directory', 'reports/junit'
    ]
    
    try:
        print(f"[PARALLEL] Starting execution for {tag_group}")
        start_time = time.time()
        
        with open(output_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, 
                                  cwd=os.getcwd(), text=True)
        
        duration = time.time() - start_time
        print(f"[PARALLEL] Completed {tag_group} in {duration:.2f}s - Exit code: {result.returncode}")
        
        return {
            'tag_group': tag_group,
            'exit_code': result.returncode,
            'duration': duration,
            'output_file': output_file
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to run {tag_group}: {e}")
        return {
            'tag_group': tag_group,
            'exit_code': -1,
            'duration': 0,
            'error': str(e),
            'output_file': output_file
        }


def main():
    parser = argparse.ArgumentParser(description='Run Banking API BDD tests in parallel')
    parser.add_argument('--processes', '-p', type=int, default=4,
                      help='Number of parallel processes (default: 4)')
    parser.add_argument('--tags', nargs='+', 
                      default=['@smoke', '@regression', '@error_handling', '@performance'],
                      help='Tag groups to run in parallel')
    parser.add_argument('--output-dir', default='parallel_outputs',
                      help='Directory for parallel execution outputs')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs('reports/junit', exist_ok=True)
    
    print(f"[PARALLEL] Banking API BDD Framework - Parallel Execution")
    print(f"[PARALLEL] Processes: {args.processes}")
    print(f"[PARALLEL] Tag groups: {args.tags}")
    print(f"[PARALLEL] Output directory: {args.output_dir}")
    print("=" * 80)
    
    start_time = time.time()
    results = []
    
    # Run tag groups in parallel
    with ProcessPoolExecutor(max_workers=args.processes) as executor:
        # Submit all tasks
        future_to_tag = {
            executor.submit(run_tag_group, tag, args.output_dir): tag 
            for tag in args.tags
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_tag):
            tag = future_to_tag[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"[ERROR] Tag group {tag} generated an exception: {e}")
                results.append({
                    'tag_group': tag,
                    'exit_code': -1,
                    'duration': 0,
                    'error': str(e)
                })
    
    total_duration = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 80)
    print("[PARALLEL] EXECUTION SUMMARY")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for result in results:
        status = "✅ PASSED" if result['exit_code'] == 0 else "❌ FAILED"
        print(f"{status} {result['tag_group']} - {result['duration']:.2f}s")
        if 'output_file' in result:
            print(f"   📄 Output: {result['output_file']}")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        
        if result['exit_code'] == 0:
            successful += 1
        else:
            failed += 1
    
    print(f"\n[RESULTS] Total execution time: {total_duration:.2f}s")
    print(f"[RESULTS] Successful: {successful}")
    print(f"[RESULTS] Failed: {failed}")
    print(f"[RESULTS] JUnit reports: reports/junit/")
    print("=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()