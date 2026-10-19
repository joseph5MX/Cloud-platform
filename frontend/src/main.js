import "./style.css";
import { initAuth, isAdmin, username, logout } from "./auth.js";
import { CONFIG } from "./config.js";
import { listServices, createService, deleteService, listAudit } from "./api.js";

const $ = (id) => document.getElementById(id);
const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
const esc = (v) => String(v).replace(/[&<>"']/g, (c) => ESC[c]);

function message(text, isError = false) {
  const el = $("msg");
  el.textContent = text;
  el.className = isError ? "msg-error" : "msg-ok";
}

function renderServices(services, admin) {
  $("svc-body").innerHTML = services.length
    ? services.map((s) => `
      <tr>
        <td>${esc(s.name)}</td>
        <td>${esc(s.image)}</td>
        <td><span class="status ${esc(s.status)}">${esc(s.status)}</span></td>
        <td>${esc(s.storage_location)}</td>
        <td>${new Date(s.created_at).toLocaleString()}</td>
        <td>${admin ? `<button class="danger" data-id="${s.id}">Delete</button>` : ""}</td>
      </tr>`).join("")
    : '<tr><td colspan="6">No services yet.</td></tr>';
}

function renderAudit(entries) {
  $("audit-body").innerHTML = entries.map((e) => `
    <tr>
      <td>${new Date(e.timestamp).toLocaleString()}</td>
      <td>${esc(e.actor)}</td>
      <td>${esc(e.action)}</td>
      <td>${esc(e.resource)}</td>
    </tr>`).join("");
}

async function refresh(admin) {
  try {
    renderServices(await listServices(), admin);
    if (admin) renderAudit(await listAudit());
  } catch (err) {
    message("Could not load data: " + err.message, true);
  }
}

async function start() {
  await initAuth();
  const admin = isAdmin();
  $("who").textContent = username();
  $("role").textContent = admin ? "admin" : "customer";
  $("logout").addEventListener("click", logout);
  $("create-section").hidden = !admin;
  $("audit-section").hidden = !admin;

  $("create-btn").addEventListener("click", async () => {
    const name = $("svc-name").value.trim();
    if (!/^[a-z0-9-]{3,30}$/.test(name)) {
      return message("Name: 3-30 chars, lowercase letters, numbers, hyphens.", true);
    }
    try {
      await createService(name, $("svc-image").value);
      $("svc-name").value = "";
      message("Service requested.");
      refresh(admin);
    } catch (err) {
      message("Create failed: " + err.message, true);
    }
  });

  $("svc-body").addEventListener("click", async (e) => {
    const id = e.target.dataset.id;
    if (!id || !confirm("Delete this service?")) return;
    try {
      await deleteService(Number(id));
      refresh(admin);
    } catch (err) {
      message("Delete failed: " + err.message, true);
    }
  });

  refresh(admin);
  setInterval(() => refresh(admin), CONFIG.POLL_MS);
}

start();
