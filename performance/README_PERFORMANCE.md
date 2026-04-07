# Mobile Backend Performance Testing

This directory contains `k6` scripts for load and performance testing of the mobile application's backend APIs.

While Appium helps us automate mobile functional testing, true concurrency and load testing are best directed right at the server APIs using tools like k6.

## Pre-requisites
1. Install k6 (Mac via Homebrew):
   ```bash
   brew install k6
   ```

## Running Tests

You can pass your actual backend API host via the `API_HOST` environment variable.

**Run Load Test**
```bash
k6 run -e API_HOST=https://your-mobile-api.com performance/scripts/load_test.js
```

**Run Spike Test**
```bash
k6 run -e API_HOST=https://your-mobile-api.com performance/scripts/spike_test.js
```

## Structure
- `load_test.js`: Checks normal ramp-up traffic sustainability.
- `spike_test.js`: Validates app backend stability against sudden bursts in traffic.
