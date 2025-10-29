#!/usr/bin/env python3
"""
LambdaTest Test Runner
This script runs tests using LambdaTest cloud platform.
"""

import subprocess
import sys
import os
import shutil

def backup_conftest():
    """Backup existing conftest.py and use LambdaTest version"""
    conftest_path = "tests/conftest.py"
    conftest_backup = "tests/conftest_local.py"
    conftest_lambdatest = "tests/conftest_lambdatest.py"
    
    if os.path.exists(conftest_path):
        print("Backing up local conftest.py to conftest_local.py")
        shutil.copy2(conftest_path, conftest_backup)
    
    if os.path.exists(conftest_lambdatest):
        print("Using LambdaTest conftest")
        shutil.copy2(conftest_lambdatest, conftest_path)

def restore_conftest():
    """Restore original conftest.py"""
    conftest_path = "tests/conftest.py"
    conftest_local = "tests/conftest_local.py"
    
    if os.path.exists(conftest_local):
        print("Restoring local conftest.py")
        shutil.copy2(conftest_local, conftest_path)

def main():
    # Check if LambdaTest credentials are set
    from utils.config import get_lambdatest_config
    
    try:
        config = get_lambdatest_config()
        if config["username"] == "YOUR_LAMBDATEST_USERNAME":
            print("\n⚠️  ERROR: LambdaTest credentials not configured!")
            print("Please update config/properties.ini with your LambdaTest credentials:")
            print("  [LambdaTest]")
            print("  username = YOUR_LAMBDATEST_USERNAME")
            print("  access_key = YOUR_LAMBDATEST_ACCESS_KEY\n")
            sys.exit(1)
    except Exception as e:
        print(f"Error reading LambdaTest configuration: {e}")
        sys.exit(1)
    
    # Backup and setup conftest
    backup_conftest()
    
    try:
        # Get test file from command line arguments
        test_file = sys.argv[1] if len(sys.argv) > 1 else "tests/test_android/test_sample.py"
        
        print(f"\n🚀 Starting LambdaTest tests...")
        print(f"📱 Test file: {test_file}\n")
        
        # Run pytest
        cmd = [
            "pytest",
            test_file,
            "-v",
            "--tb=short",
            "--alluredir=reports/allure-results",
            "-v"
        ]
        
        result = subprocess.run(cmd)
        
        return result.returncode
    finally:
        # Always restore original conftest
        restore_conftest()

if __name__ == "__main__":
    sys.exit(main())

