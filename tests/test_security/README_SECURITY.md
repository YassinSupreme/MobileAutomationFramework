# Mobile API Security Testing

This directory contains automated security tests that target your mobile application's backend APIs (`API_HOST` in `config/properties.ini`).

These tests validate that the app's backend is resilient against the most common vulnerabilities (OWASP Top 10) that attackers might perform when intercepting mobile app traffic.

## What is tested?
1. **SQL Injection**: Injecting malicious SQL syntax into login/data endpoints.
2. **Cross-Site Scripting (XSS)**: Injecting JavaScript into profiles to ensure proper sanitization.
3. **Path Traversal**: Attempting to read sensitive server files (e.g., `/etc/passwd`).
4. **Security Headers**: Verifying the presence of critical HTTP headers to protect against sniffing and man-in-the-middle attacks.

## Pre-requisites
Make sure you have `pytest` and `requests` installed:
```bash
pip install pytest requests
```

## How to run
You can run the security suite independently using `pytest`:

```bash
pytest tests/test_security/test_api_security.py -v -s
```

*Note: For comprehensive security assessments, these tests should be paired with dynamic/static mobile analysis tools like **MobSF** (Mobile Security Framework).*
