import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEYCLOAK = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.environ.get("KEYCLOAK_REALM", "Cloudplatform")
API = os.environ.get("API_URL", "http://localhost:8000")
CLIENT = "cloud-frontend"


def send(req):
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def get_token(username, password):
    data = urllib.parse.urlencode({
        "client_id": CLIENT, "grant_type": "password",
        "username": username, "password": password}).encode()
    url = f"{KEYCLOAK}/realms/{REALM}/protocol/openid-connect/token"
    return send(urllib.request.Request(url, data=data))


def call_api(path, token, method="GET", body=None):
    headers = {"Authorization": "Bearer " + token}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data,
                                 headers=headers, method=method)
    return send(req)


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "admin1"
    password = getpass.getpass(f"Password for {username}: ")

    status, text = get_token(username, password)
    print("Keycloak token request:", status)
    if status != 200:
        print("Keycloak said:", text)
        sys.exit(1)
    token = json.loads(text)["access_token"]
    print("Token length:", len(token))

    status, text = call_api("/me", token)
    print("Backend /me:", status, text)
    if status != 200 or "--full" not in sys.argv:
        return

    print("\nCreating service web-01 ...")
    status, text = call_api("/services", token, "POST",
                            {"name": "web-01", "image": "nginx:alpine"})
    print("POST /services:", status, text)
    if status != 201:
        return
    service_id = json.loads(text)["id"]

    for _ in range(12):
        time.sleep(5)
        status, text = call_api("/services", token)
        if status != 200:
            print("GET /services:", status, text)
            break
        current = [s for s in json.loads(text) if s["id"] == service_id]
        state = current[0]["status"] if current else "missing"
        print("  status:", state)
        if state in ("running", "error"):
            break

    status, text = call_api("/audit", token)
    print("GET /audit:", status, text[:300])
    status, _ = call_api(f"/services/{service_id}", token, "DELETE")
    print("DELETE /services:", status, "(204 = success)")


main()
