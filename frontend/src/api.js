import { CONFIG } from "./config.js";
import { getToken, username } from "./auth.js";

// ---------- Mock data (used while USE_MOCK is true) ----------
const LOCATION = "Botswana (local server)";
let nextId = 2;
let mockServices = [
  { id: 1, name: "demo-web", image: "nginx:alpine", status: "running",
    storage_location: LOCATION, created_at: new Date().toISOString() },
];
let mockAudit = [];

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

function logMock(action, resource) {
  mockAudit.unshift({ timestamp: new Date().toISOString(),
    actor: username(), action, resource });
}

// ---------- Helper for real backend calls ----------
async function call(path, options = {}) {
  const token = await getToken();
  const res = await fetch(CONFIG.API_URL + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token,
    },
  });
  if (!res.ok) throw new Error("API returned " + res.status);
  return res.status === 204 ? null : res.json();
}

// ---------- Functions the page uses ----------
export async function listServices() {
  if (CONFIG.USE_MOCK) { await wait(150); return structuredClone(mockServices); }
  return call("/services");
}

export async function createService(name, image) {
  if (CONFIG.USE_MOCK) {
    await wait(300);
    const svc = { id: nextId++, name, image, status: "provisioning",
      storage_location: LOCATION, created_at: new Date().toISOString() };
    mockServices.push(svc);
    logMock("CREATE", "service:" + name);
    setTimeout(() => { svc.status = "running"; }, 4000);
    return svc;
  }
  return call("/services", { method: "POST", body: JSON.stringify({ name, image }) });
}

export async function deleteService(id) {
  if (CONFIG.USE_MOCK) {
    await wait(200);
    const svc = mockServices.find((s) => s.id === id);
    mockServices = mockServices.filter((s) => s.id !== id);
    if (svc) logMock("DELETE", "service:" + svc.name);
    return null;
  }
  return call("/services/" + id, { method: "DELETE" });
}

export async function listAudit() {
  if (CONFIG.USE_MOCK) { await wait(150); return structuredClone(mockAudit); }
  return call("/audit");
}
