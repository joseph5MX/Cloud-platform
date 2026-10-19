export const CONFIG = {
  KEYCLOAK_URL: "http://SERVER-IP:8080",
  REALM: "cloudplatform",
  CLIENT_ID: "cloud-frontend",
  API_URL: "http://SERVER-IP:8000", // backend address (used when USE_MOCK is false)
  USE_MOCK: true,                   // true = fake data, no backend needed
  POLL_MS: 5000,                    // how often the table refreshes
};
