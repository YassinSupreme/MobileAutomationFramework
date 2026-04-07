import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

/**
 * k6 API Performance Test for Mobile Backend
 * ------------------------------------------
 * Note: Mobile UI automation (Appium) measures frontend responsiveness.
 * For load testing, we target the backend APIs directly via k6.
 * 
 * Replace 'API_BASE_URL' with your actual mobile backend endpoint
 * (e.g., the endpoints accessed by the General-Store app).
 */

// Custom metrics
const errorRate = new Rate('errors');
const responseTimeTrend = new Trend('response_time');

export const options = {
  // Load test stages
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 Users
    { duration: '1m',  target: 10 },  // Stay at 10 Users for 1 minute
    { duration: '30s', target: 0 },   // Ramp down to 0 Users
  ],
  thresholds: {
    // Assertions on the test results
    http_req_duration: ['p(95)<1000'], // 95% of requests must complete under 1000ms
    http_req_failed: ['rate<0.05'],    // Error rate must be less than 5%
  },
};

// Use an environment variable or default to a dummy API
const BASE_URL = __ENV.API_HOST || 'https://reqres.in/api';

export default function () {
  // Example GET Request 
  // (Replace with actual endpoint, e.g., fetching product list for the General Store app)
  const res = http.get(`${BASE_URL}/users?page=1`);

  // Assertions (Checks)
  const success = check(res, {
    'status is 200': (r) => r.status === 200,
    'latency is under 1000ms': (r) => r.timings.duration < 1000,
    'body is not empty': (r) => r.body && r.body.length > 0,
  });

  if (!success) {
    errorRate.add(1);
  }
  
  responseTimeTrend.add(res.timings.duration);

  // Think time between requests to simulate real app user behavior
  sleep(1);
}
