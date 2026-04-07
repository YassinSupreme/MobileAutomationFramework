import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * k6 Spike Test — Simulating sudden traffic surge.
 */

export const options = {
  stages: [
    { duration: '10s', target: 5 },    // Baseline small traffic
    { duration: '5s', target: 100 },   // SPIKE: sudden surge to 100 users
    { duration: '30s', target: 100 },  // Sustain the surge
    { duration: '10s', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // Lenient threshold for spikes
    http_req_failed: ['rate<0.1'],     // Allow max 10% failure during spike
  },
};

const BASE_URL = __ENV.API_HOST || 'https://reqres.in/api';

export default function () {
  const res = http.get(`${BASE_URL}/users/2`);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(0.5);
}
