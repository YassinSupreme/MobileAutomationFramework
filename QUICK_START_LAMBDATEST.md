# Quick Start: Running Tests on LambdaTest

## 🔧 Setup (One-time)

1. **Get LambdaTest Credentials**
   - Sign up at https://www.lambdatest.com/
   - Go to https://automation.lambdatest.com/build
   - Copy your Username and Access Key

2. **Update Configuration**
   Edit `config/properties.ini` and update the LambdaTest section:
   ```ini
   [LambdaTest]
   username = your_actual_username_here
   access_key = your_actual_access_key_here
   ```

## 🚀 Run Tests

### Method 1: Using the Runner Script (Recommended)
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python run_lambdatest_tests.py

# Or run specific test file
python run_lambdatest_tests.py tests/test_android/test_sample.py
```

### Method 2: Manual Pytest
```bash
# Backup current conftest
cp tests/conftest.py tests/conftest_local.py

# Use LambdaTest conftest
cp tests/conftest_lambdatest.py tests/conftest.py

# Run tests
pytest tests/test_android/test_sample.py -v --alluredir=reports/allure-results

# Restore local conftest
cp tests/conftest_local.py tests/conftest.py
```

## 📱 Configure Devices

You can change the device in `config/properties.ini`:
- `device_name`: Device model (e.g., "Samsung Galaxy S23 Ultra")
- `platform_version`: Android version (e.g., "13")

Available devices: https://www.lambdatest.com/list-of-browsers

## 📊 View Results

- LambdaTest Dashboard: https://automation.lambdatest.com/
- Screenshots: `reports/screenshots/failed/`
- Allure Reports: `allure serve reports/allure-results`

## 💡 Tips

- Make sure you have sufficient LambdaTest credits
- The APK will be uploaded automatically to LambdaTest
- Tests run on real devices in the cloud
- You can run tests in parallel by using pytest-xdist

## 🔄 Switch Between Local and LambdaTest

To run locally:
```bash
pytest tests/test_android/test_sample.py -v
```

To run on LambdaTest:
```bash
python run_lambdatest_tests.py tests/test_android/test_sample.py
```

