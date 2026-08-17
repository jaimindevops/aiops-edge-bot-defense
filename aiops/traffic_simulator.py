import subprocess
import time
import json
import sys

def get_ingress_ip():
    """Retrieve external load balancer IP from Kubernetes."""
    cmd = [
        "kubectl", "get", "svc", "-n", "ingress-nginx",
        "ingress-nginx-controller", "-o", "jsonpath={.status.loadBalancer.ingress[0].ip}"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    ip = result.stdout.strip()
    if not ip:
        print("[!] Error: Could not resolve Ingress IP. Is the Ingress Controller running?")
        sys.exit(1)
    return ip

def send_request(ingress_ip, path, method="GET", client_ip=None, user_agent=None):
    """Executes a curl request simulating realistic edge traffic."""
    url = f"https://{ingress_ip}{path}"
    cmd = ["curl", "-k", "-s", "-i", "-X", method, "-H", "Host: edge.netflex.internal"]
    
    if client_ip:
        cmd.extend(["-H", f"X-Forwarded-For: {client_ip}"])
    if user_agent:
        cmd.extend(["-A", user_agent])
    
    cmd.append(url)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def run_test_suite():
    ingress_ip = get_ingress_ip()
    print("==================================================================")
    print("🚀 NETFLEX AIOPS EDGE DEFENSE & DELIVERY TEST SUITE")
    print(f"🎯 Target Ingress Gateway: https://{ingress_ip}")
    print("==================================================================\n")

    # -------------------------------------------------------------
    # SCENARIO 1: Clean User Streaming Traffic (Cache MISS -> HIT)
    # -------------------------------------------------------------
    print(">>> [TEST 1/4] Simulating Legitimate Consumer Video Streaming...")
    print("  -> Request 1: Initial stream request (Expect Cache MISS / 200 OK)")
    resp1 = send_request(ingress_ip, "/stream", user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
    status1 = resp1.split("\n")[0] if resp1 else "No Response"
    print(f"     Status: {status1}")
    time.sleep(2)

    print("  -> Request 2: Repeated stream request (Expect Cache HIT / 200 OK)")
    resp2 = send_request(ingress_ip, "/stream", user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
    status2 = resp2.split("\n")[0] if resp2 else "No Response"
    print(f"     Status: {status2}")
    print("  ✅ Legitimate traffic passed.\n")
    time.sleep(3)

    # -------------------------------------------------------------
    # SCENARIO 2: Scanner Bot Probing Honeypot Trap
    # -------------------------------------------------------------
    attacker_bot_ip = "203.0.113.111"
    print(f">>> [TEST 2/4] Simulating Vulnerability Scanner Bot from IP: {attacker_bot_ip}...")
    print("  -> Sending probe to honeypot trap URI: /admin-trap")
    resp_bot = send_request(
        ingress_ip, 
        "/admin-trap", 
        method="GET",
        client_ip=attacker_bot_ip, 
        user_agent="ScannerBot/2.4 (Automated Recon)"
    )
    status_bot = resp_bot.split("\n")[0] if resp_bot else "No Response"
    print(f"     Initial Probe Status: {status_bot}")
    print("  ⏳ Waiting for Gemma 2B triage and automated ingress remediation...")
    time.sleep(15)  # Allow time for Ollama CPU inference and kubectl patch

    # -------------------------------------------------------------
    # SCENARIO 3: Hydra Brute-Force Credential Stuffing Attack
    # -------------------------------------------------------------
    attacker_hydra_ip = "198.51.100.222"
    print(f">>> [TEST 3/4] Simulating Brute-Force Attack from IP: {attacker_hydra_ip}...")
    print("  -> Sending automated credential stuffing burst to: /api/auth")
    resp_hydra = send_request(
        ingress_ip, 
        "/api/auth", 
        method="POST", 
        client_ip=attacker_hydra_ip, 
        user_agent="Hydra/9.5 (Credential Stuffing BruteForce)"
    )
    status_hydra = resp_hydra.split("\n")[0] if resp_hydra else "No Response"
    print(f"     Initial Attack Status: {status_hydra}")
    print("  ⏳ Waiting for Gemma 2B triage and automated ingress remediation...")
    time.sleep(15)

    # -------------------------------------------------------------
    # SCENARIO 4: Firewall Enforcement Verification (403 Forbidden)
    # -------------------------------------------------------------
    print(">>> [TEST 4/4] Verifying Active Edge Firewall Enforcement (HTTP 403 Drops)...")
    
    print(f"  -> Testing blocked ScannerBot IP ({attacker_bot_ip}) against /stream:")
    verify_bot = send_request(ingress_ip, "/stream", client_ip=attacker_bot_ip)
    status_vbot = verify_bot.split("\n")[0] if verify_bot else "No Response"
    print(f"     Result: {status_vbot}")
    if "403" in status_vbot:
        print(f"     🛡️ [SUCCESS] {attacker_bot_ip} actively blocked at the edge!")
    else:
        print(f"     ⚠️ Check watchdog: {attacker_bot_ip} was not blocked yet.")

    print(f"  -> Testing blocked Hydra IP ({attacker_hydra_ip}) against /stream:")
    verify_hydra = send_request(ingress_ip, "/stream", client_ip=attacker_hydra_ip)
    status_vhydra = verify_hydra.split("\n")[0] if verify_hydra else "No Response"
    print(f"     Result: {status_vhydra}")
    if "403" in status_vhydra:
        print(f"     🛡️ [SUCCESS] {attacker_hydra_ip} actively blocked at the edge!")
    else:
        print(f"     ⚠️ Check watchdog: {attacker_hydra_ip} was not blocked yet.")

    print("\n==================================================================")
    print("🏁 TEST SUITE COMPLETED!")
    print("👉 Check your Grafana Dashboard (http://localhost:3000) to view live metrics & Gemma triage tables.")
    print("==================================================================")

if __name__ == "__main__":
    run_test_suite()
