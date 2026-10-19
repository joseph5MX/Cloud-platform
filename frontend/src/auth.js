import Keycloak from "keycloak-js";
import { CONFIG } from "./config.js";

const keycloak = new Keycloak({
  url: CONFIG.KEYCLOAK_URL,
  realm: CONFIG.REALM,
  clientId: CONFIG.CLIENT_ID,
});

export async function initAuth() {
  const ok = await keycloak.init({
    onLoad: "login-required",
    // PKCE needs a secure context (HTTPS or localhost); fall back on plain HTTP
    pkceMethod: window.isSecureContext ? "S256" : false,
    checkLoginIframe: false,
  });
  if (!ok) await keycloak.login();
  setInterval(() => keycloak.updateToken(30).catch(() => keycloak.login()), 20000);
}

export async function getToken() {
  await keycloak.updateToken(30);
  return keycloak.token;
}

export const isAdmin = () => keycloak.hasRealmRole("admin");
export const username = () => keycloak.tokenParsed?.preferred_username;
export const logout = () => keycloak.logout({ redirectUri: window.location.origin });
