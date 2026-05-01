import http from "k6/http";
import { check, sleep } from "k6";

// Override with BASE_URL=http://localhost:5001 when using a different port.
const BASE_URL = __ENV.BASE_URL || "http://localhost:5000";

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "2m", target: 30 },
    { duration: "1m", target: 30 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],
  },
};

export default function () {
  const response = http.get(`${BASE_URL}/cpu-load?seconds=2`);

  check(response, {
    "cpu load endpoint returned 200": (res) => res.status === 200,
  });

  sleep(1);
}
