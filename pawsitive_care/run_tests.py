#!/usr/bin/env python
"""
Test Runner for Pawsitive Care
This script runs comprehensive tests for all apps and generates a detailed report.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line
from io import StringIO
import time
from datetime import datetime


class TestRunner:
    """Custom test runner with detailed reporting"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def setup_django(self):
        """Setup Django environment"""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawsitive_care.settings')
        django.setup()
        
    def run_app_tests(self, app_name):
        """Run tests for a specific app"""
        print(f"\n{'='*60}")
        print(f"Running tests for {app_name.upper()} app")
        print(f"{'='*60}")
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            TestRunner = get_runner(settings)
            test_runner = TestRunner(verbosity=2, interactive=False)
            
            if app_name == 'all_apps':
                failures = test_runner.run_tests(['test_all_apps'])
            else:
                failures = test_runner.run_tests([f'{app_name}.tests'])
            
            output = sys.stdout.getvalue()
            
        except Exception as e:
            failures = 1
            output = f"Error running tests: {str(e)}"
        finally:
            sys.stdout = old_stdout
            
        # Store results
        self.test_results[app_name] = {
            'failures': failures,
            'output': output,
            'status': 'PASSED' if failures == 0 else 'FAILED'
        }
        
        # Print summary
        status = 'PASSED' if failures == 0 else 'FAILED'
        print(f"Tests for {app_name}: {status}")
        if failures > 0:
            print(f"Failures: {failures}")
            
        return failures
        
    def run_all_tests(self):
        """Run tests for all apps"""
        self.start_time = time.time()
        
        print("Starting Comprehensive Test Suite for Pawsitive Care")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "="*80)
        
        # List of apps to test
        apps_to_test = [
            'accounts',
            'pets', 
            'appointments',
            'billing',
            'inventory',
            'petmedia',
            'communication',
            'records',
            'all_apps'  # Our comprehensive test file
        ]
        
        total_failures = 0
        
        for app in apps_to_test:
            try:
                failures = self.run_app_tests(app)
                total_failures += failures
            except Exception as e:
                print(f"Error testing {app}: {str(e)}")
                total_failures += 1
                self.test_results[app] = {
                    'failures': 1,
                    'output': f"Error: {str(e)}",
                    'status': 'ERROR'
                }
        
        self.end_time = time.time()
        self.generate_report(total_failures)
        
        return total_failures
        
    def generate_report(self, total_failures):
        """Generate a comprehensive test report"""
        duration = self.end_time - self.start_time
        
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        print(f"Test Duration: {duration:.2f} seconds")
        print(f"Total Test Status: {'PASSED' if total_failures == 0 else 'FAILED'}")
        print(f"Total Failures: {total_failures}")
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nPER-APP TEST RESULTS:")
        print("-" * 50)
        
        for app, results in self.test_results.items():
            status_emoji = "✅" if results['status'] == 'PASSED' else "❌"
            print(f"{status_emoji} {app.upper()}: {results['status']}")
            if results['failures'] > 0:
                print(f"   Failures: {results['failures']}")
        
        # Generate detailed HTML report
        self.generate_html_report(total_failures, duration)
        
        print(f"\nDetailed HTML report saved to: test_report.html")
        
    def generate_html_report(self, total_failures, duration):
        """Generate an HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pawsitive Care - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .passed {{ color: #27ae60; font-weight: bold; }}
        .failed {{ color: #e74c3c; font-weight: bold; }}
        .error {{ color: #f39c12; font-weight: bold; }}
        .app-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; }}
        .test-output {{ background-color: #f8f9fa; padding: 10px; margin: 10px 0; 
                       border-radius: 3px; font-family: monospace; font-size: 12px; 
                       max-height: 300px; overflow-y: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐾 Pawsitive Care - Comprehensive Test Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <p><strong>Duration:</strong> {duration:.2f} seconds</p>
        <p><strong>Overall Status:</strong> 
           <span class="{'passed' if total_failures == 0 else 'failed'}">
               {'PASSED' if total_failures == 0 else 'FAILED'}
           </span>
        </p>
        <p><strong>Total Failures:</strong> {total_failures}</p>
        <p><strong>Apps Tested:</strong> {len(self.test_results)}</p>
    </div>
    
    <h2>Detailed Results</h2>
    <table>
        <thead>
            <tr>
                <th>App</th>
                <th>Status</th>
                <th>Failures</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for app, results in self.test_results.items():
            status_class = results['status'].lower()
            html_content += f"""
            <tr>
                <td><strong>{app.upper()}</strong></td>
                <td><span class="{status_class}">{results['status']}</span></td>
                <td>{results['failures']}</td>
                <td>
                    <details>
                        <summary>View Output</summary>
                        <div class="test-output">{results['output'][:1000]}{'...' if len(results['output']) > 1000 else ''}</div>
                    </details>
                </td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
    
    <div class="summary">
        <h3>Test Coverage Areas</h3>
        <ul>
            <li><strong>Accounts App:</strong> User management, authentication, role-based access</li>
            <li><strong>Pets App:</strong> Pet management, medical records, document handling</li>
            <li><strong>Appointments App:</strong> Scheduling, vet assignments, status management</li>
            <li><strong>Billing App:</strong> Payment processing, service costs, billing status</li>
            <li><strong>Inventory App:</strong> Stock management, suppliers, purchase orders</li>
            <li><strong>PetMedia App:</strong> Blog posts, categories, comments system</li>
            <li><strong>Communication App:</strong> Messaging system (if implemented)</li>
            <li><strong>Records App:</strong> Medical records management (if implemented)</li>
            <li><strong>Integration Tests:</strong> Cross-app functionality and workflows</li>
            <li><strong>Security Tests:</strong> Authorization, data protection</li>
            <li><strong>Performance Tests:</strong> Query optimization, database efficiency</li>
        </ul>
    </div>
    
    <div class="summary">
        <h3>Next Steps</h3>
        <p>If any tests failed, please review the detailed output above and:</p>
        <ul>
            <li>Check for missing dependencies or configuration issues</li>
            <li>Verify database migrations are up to date</li>
            <li>Ensure all required model fields are properly defined</li>
            <li>Review URL patterns and view implementations</li>
            <li>Check for any permission or authentication issues</li>
        </ul>
    </div>
</body>
</html>
"""
        
        with open('test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Main function to run tests"""
    print("Pawsitive Care - Comprehensive Test Suite")
    print("="*50)
    
    runner = TestRunner()
    runner.setup_django()
    
    try:
        failures = runner.run_all_tests()
        
        if failures == 0:
            print("\n🎉 All tests passed successfully!")
            return 0
        else:
            print(f"\n❌ {failures} test(s) failed. Check the report for details.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Error running test suite: {str(e)}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
