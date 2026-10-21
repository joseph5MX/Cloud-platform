import { CONFIG } from "./config.js";
import { getToken, username, isAdmin } from "./auth.js";

// ---------- Mock data (used while USE_MOCK is true) ----------
const LOCATION = "Botswana (local server)";
const MOCK_CUSTOMERS = [{ id: "mock-customer-1", username: "customer1" }];
let nextId = 2;
let mockServices = [
  { id: 1, name: "demo-web", owner: "customer1", image: "nginx:alpine",
    status: "running", storage_location: LOCATION, port: null, url: null,
    created_at: new Date().toISOString() },
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
  if (CONFIG.USE_MOCK) {
    await wait(150);
    const rows = isAdmin()
      ? mockServices
      : mockServices.filter((s) => s.owner === username());
    return structuredClone(rows);
  }
  return call("/services");
}

export async function listCustomers() {
  if (CONFIG.USE_MOCK) {
    await wait(100);
    return structuredClone(MOCK_CUSTOMERS);
  }
  return call("/customers");
}

export async function createService(name, image, ownerId) {
  if (CONFIG.USE_MOCK) {
    await wait(300);
    const owner = MOCK_CUSTOMERS.find((c) => c.id === ownerId);
    const svc = { id: nextId++, name, image,
      owner: owner ? owner.username : username(),
      status: "provisioning", storage_location: LOCATION, port: null,
      url: null, created_at: new Date().toISOString() };
    mockServices.push(svc);
    logMock("CREATE", "service:" + name + " (owner: " + svc.owner + ")");
    setTimeout(() => { svc.status = "running"; }, 4000);
    return svc;
  }
  return call("/services", {
    method: "POST",
    body: JSON.stringify({ name, image, owner_id: ownerId || null }),
  });
}

export async function deleteService(id) {
  if (CONFIG.USE_MOCK) {
    await wait(200);
    const svc = mockServices.find((s) => s.id === id);
    mockServices = mockServices.filter((s) => s.id !== id);
    if (svc) logMock("DELETE", "service:" + svc.name + " (owner: " + svc.owner + ")");
    return null;
  }
  return call("/services/" + id, { method: "DELETE" });
}

export async function listAudit() {
  if (CONFIG.USE_MOCK) {
    await wait(150);
    return structuredClone(mockAudit);
  }
  return call("/audit");
}
