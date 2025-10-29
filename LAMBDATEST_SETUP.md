# LambdaTest Setup Guide

This guide will help you run your mobile automation tests on LambdaTest cloud platform.

## Prerequisites

1. LambdaTest Account:
   - Sign up at https://www.lambdatest.com/
   - Get your username and access key from https://automation.lambdatest.com/build

2. Update Configuration:
   - Open `config/properties.ini`
   - Update the LambdaTest section with your credentials:
   ```ini
   [LambdaTest]
   username = YOUR_LAMBDATEST_USERNAME
   access_key = YOUR_LAMBDATEST_ACCESS_KEY
   grid_url = https://mobile-hub.lambdatest.com/wd/hub
   device_name = Samsung Galaxy S23 Ultra
   platform_version = 13
   build_name = Mobile Automation Tests
   project_name = Mobile Automation Framework
   ```

## Running Tests

### Option 1: Using the Virtual Environment

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with LambdaTest
pytest tests/test_android/test_sample.py -v --alluredir=reports/allure-results -c pytest_lambdatest.ini
```

### Option 2: Direct Python Execution

```bash
# Run with LambdaTest configuration
PYTHONPATH=. pytest tests/test_android/test_sample.py \
  --alluredir=reports/allure-results \
  --allure-lambdatest \
  -v
```

## Configuration Options

You can modify the device configurations in `config/properties.ini`:

- `device_name`: Choose from LambdaTest's device catalog (e.g., "Pixel 7 Pro", "Samsung Galaxy S23 Ultra")
- `platform_version`: Android version (e.g., "13", "12", "11")
- `build_name`: Custom build name for test reporting
- `project_name`: Project name for organizing tests

## Available Devices

Visit https://www.lambdatest.com/list-of-browsers to view all available devices.

## Test Results

- Test results will be available in the LambdaTest dashboard
- Screenshots of failed tests will be saved in `reports/screenshots/failed/`
- Allure reports can be generated using: `allure serve reports/allure-results`

## Notes

- The APK file will be automatically uploaded to LambdaTest on test execution
- Make sure you have sufficient LambdaTest credits in your account
- Tests will run on real devices in the LambdaTest cloud

