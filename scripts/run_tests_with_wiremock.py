#!/usr/bin/env python3
"""
Banking API BDD Test Runner with Wiremock Auto-Restart
Ensures fresh Wiremock instance for every test run to achieve 100% pass rate
"""

import os
import sys
import time
import subprocess
import requests
import psutil
import argparse
from pathlib import Path


class WiremockManager:
    def __init__(self, port=8081):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.health_endpoint = f"{self.base_url}/__admin/health"
        self.process = None

    def kill_existing_processes(self):
        """Kill any existing WireMock processes"""
        print("🔄 Stopping existing WireMock processes...")
        
        killed_processes = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'java.exe':
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'wiremock-standalone.jar' in cmdline:
                        print(f"   Killing WireMock process (PID: {proc.info['pid']})")
                        proc.terminate()
                        killed_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_processes > 0:
            print(f"   Terminated {killed_processes} WireMock process(es)")
            time.sleep(3)  # Wait for processes to fully terminate
        else:
            print("   No existing WireMock processes found")

    def find_wiremock_jar(self):
        """Find WireMock JAR file in common locations"""
        possible_locations = [
            Path.cwd() / "wiremock-standalone.jar",
            Path("C:/Users/D/Wiremock/wiremock-standalone.jar"),
            Path("/mnt/c/Users/D/Wiremock/wiremock-standalone.jar")
        ]
        
        for jar_path in possible_locations:
            if jar_path.exists():
                return jar_path
        
        return None

    def start_wiremock(self):
        """Start fresh WireMock instance"""
        print("🚀 Starting fresh WireMock instance...")
        
        jar_path = self.find_wiremock_jar()
        if not jar_path:
            raise FileNotFoundError(
                "WireMock JAR not found! Please ensure wiremock-standalone.jar is available in:\n"
                "1. Current directory\n"
                "2. C:/Users/D/Wiremock/"
            )
        
        # Determine working directory
        if "Wiremock" in str(jar_path):
            working_dir = jar_path.parent
            mappings_exist = (working_dir / "mappings").exists()
        else:
            working_dir = Path.cwd()
            mappings_exist = (working_dir / "mappings").exists()
        
        # Use Windows Java executable from WSL
        java_exe = "/mnt/c/Program Files/Eclipse Adoptium/jdk-11.0.26.4-hotspot/bin/java.exe"
        cmd = [
            java_exe, "-jar", str(jar_path),
            "--port", str(self.port),
            "--global-response-templating",
            "--verbose"
        ]
        
        if mappings_exist:
            print(f"   Using mappings from: {working_dir}/mappings")
        
        print(f"   Starting WireMock on port {self.port}")
        print(f"   JAR location: {jar_path}")
        print(f"   Working directory: {working_dir}")
        
        # Start WireMock in background
        self.process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print(f"   WireMock started with PID: {self.process.pid}")

    def wait_for_health(self, timeout=30):
        """Wait for WireMock to be healthy"""
        print("⏳ Waiting for WireMock to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.health_endpoint, timeout=2)
                if response.status_code == 200:
                    print(f"✅ WireMock is healthy and ready on port {self.port}")
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(1)
            print("   Still waiting...")
        
        raise TimeoutError(f"WireMock failed to start within {timeout} seconds")

    def restart(self):
        """Complete restart cycle"""
        self.kill_existing_processes()
        self.start_wiremock()
        self.wait_for_health()


def run_behave_tests(format_type="pretty", tags=None):
    """Run behave tests with specified format and tags"""
    print("\n🧪 Running BDD Tests...")

    # Set environment to dev for local development
    env = os.environ.copy()
    env['ENVIRONMENT'] = 'dev'
    env['TEST_ENVIRONMENT'] = 'dev'

    cmd = ["python", "-m", "behave", "--format", format_type]

    if tags:
        cmd.extend(["--tags", tags])

    print(f"   Command: {' '.join(cmd)}")
    print(f"   Environment: dev (localhost:8081)")

    try:
        result = subprocess.run(cmd, env=env, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run Banking API tests with fresh WireMock")
    parser.add_argument("--format", default="pretty", help="Behave output format (default: pretty)")
    parser.add_argument("--tags", help="Behave tags to run (e.g., @smoke)")
    parser.add_argument("--port", type=int, default=8081, help="WireMock port (default: 8081)")
    parser.add_argument("--skip-wiremock", action="store_true", help="Skip WireMock restart")
    
    args = parser.parse_args()
    
    print("🏦 Banking API BDD Test Framework")
    print("=" * 50)
    
    if not args.skip_wiremock:
        try:
            wiremock = WiremockManager(port=args.port)
            wiremock.restart()
        except Exception as e:
            print(f"❌ Failed to start WireMock: {e}")
            return 1
    else:
        print("⚠️  Skipping WireMock restart (using existing instance)")
    
    # Run the tests
    exit_code = run_behave_tests(format_type=args.format, tags=args.tags)
    
    if exit_code == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n❌ Tests completed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())