#!/usr/bin/env python3
"""
Master Test Runner for All Microservices
Runs unit tests for all services and provides consolidated reporting
"""

import subprocess
import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services = {
            'user-service': {
                'path': 'app/user-service',
                'runner': 'tests/run-tests.js',
                'type': 'node'
            },
            'chat-service': {
                'path': 'app/chat-service', 
                'runner': 'tests/run_tests.py',
                'type': 'python'
            },
            'message-service': {
                'path': 'app/message-service',
                'runner': 'tests/run_tests.sh',
                'type': 'go'
            },
            'gateway-service': {
                'path': 'app/gateway-service',
                'runner': 'tests/run_tests.py', 
                'type': 'python'
            }
        }
        
        # Colors for output
        self.colors = {
            'red': '\033[31m',
            'green': '\033[32m', 
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'reset': '\033[0m'
        }

    def log(self, color, message):
        """Print colored log message"""
        print(f"{self.colors[color]}{message}{self.colors['reset']}")

    def run_service_tests(self, service_name, service_config):
        """Run tests for a single service"""
        service_path = self.project_root / service_config['path']
        runner_path = service_path / service_config['runner']
        
        self.log('blue', f"📋 Testing {service_name}")
        self.log('blue', "-" * 40)
        
        if not runner_path.exists():
            self.log('yellow', f"⚠️  Test runner not found: {runner_path}")
            return False, f"Test runner missing for {service_name}"
        
        try:
            # Change to service directory
            original_cwd = os.getcwd()
            os.chdir(service_path)
            
            # Make runner executable if it's a shell script
            if service_config['type'] == 'go':
                os.chmod(runner_path, 0o755)
            
            # Run the test runner
            if service_config['type'] == 'node':
                cmd = ['node', str(runner_path)]
            elif service_config['type'] == 'python':
                cmd = ['python3', str(runner_path)]
            else:  # go/shell script
                cmd = ['./' + service_config['runner']]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Restore original directory
            os.chdir(original_cwd)
            
            # Display output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            if result.returncode == 0:
                self.log('green', f"✅ {service_name} tests passed")
                return True, None
            else:
                self.log('red', f"❌ {service_name} tests failed")
                return False, f"Exit code: {result.returncode}"
                
        except subprocess.TimeoutExpired:
            self.log('red', f"⏰ {service_name} tests timed out")
            return False, "Test timeout exceeded"
        except Exception as e:
            self.log('red', f"💥 {service_name} tests crashed: {e}")
            return False, str(e)

    def run_all_tests_sequential(self):
        """Run all service tests sequentially"""
        self.log('cyan', "🚀 Starting Sequential Test Execution...")
        self.log('cyan', "=" * 50)
        
        start_time = time.time()
        results = {}
        
        for service_name, config in self.services.items():
            success, error = self.run_service_tests(service_name, config)
            results[service_name] = {
                'success': success,
                'error': error
            }
            
            # Add spacing between services
            print()
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Display summary
        self.display_summary(results, duration)
        return results

    def run_all_tests_parallel(self):
        """Run all service tests in parallel"""
        self.log('cyan', "🚀 Starting Parallel Test Execution...")
        self.log('cyan', "=" * 50)
        
        start_time = time.time()
        results = {}
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=len(self.services)) as executor:
            # Submit all tasks
            future_to_service = {
                executor.submit(self.run_service_tests, name, config): name 
                for name, config in self.services.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_service):
                service_name = future_to_service[future]
                try:
                    success, error = future.result()
                    results[service_name] = {
                        'success': success,
                        'error': error
                    }
                except Exception as e:
                    results[service_name] = {
                        'success': False,
                        'error': str(e)
                    }
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Display summary
        self.display_summary(results, duration)
        return results

    def display_summary(self, results, duration):
        """Display test results summary"""
        print("\n" + "=" * 50)
        self.log('magenta', "📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for r in results.values() if r['success'])
        failed = len(results) - passed
        
        # Service-by-service results
        for service_name, result in results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            self.log('white', f"{status} {service_name}")
            if not result['success']:
                self.log('yellow', f"     Error: {result['error']}")
        
        print()
        self.log('green', f"✅ Passed: {passed}")
        self.log('red', f"❌ Failed: {failed}")
        self.log('white', f"📋 Total: {len(results)}")
        self.log('cyan', f"⏱️  Duration: {duration:.2f} seconds")
        
        # Overall result
        if failed == 0:
            print()
            self.log('green', "🎉 All microservice tests passed!")
            return True
        else:
            print()
            self.log('red', f"💥 {failed} service(s) failed tests")
            return False

def main():
    """Main entry point"""
    runner = TestRunner()
    
    # Check if we should run in parallel
    parallel = '--parallel' in sys.argv
    
    if parallel:
        results = runner.run_all_tests_parallel()
    else:
        results = runner.run_all_tests_sequential()
    
    # Exit with appropriate code
    success = all(r['success'] for r in results.values())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()