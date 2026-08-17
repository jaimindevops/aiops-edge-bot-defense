import json
import urllib.request
from datetime import datetime

class IncidentNotifier:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url

    def emit_alert(self, ip: str, threat_type: str, confidence: float, reasoning: str):
        """
        Dispatches structured ChatOps alerts to Slack/Teams or formats for Incident Logging.
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        alert_payload = {
            "title": "🚨 [AIOps Edge Defense] Malicious Actor Remediated",
            "timestamp": timestamp,
            "blocked_ip": ip,
            "threat_classification": threat_type,
            "confidence_score": f"{confidence * 100:.1f}%",
            "llm_reasoning": reasoning,
            "status": "INGRESS_DENY_RULE_APPLIED"
        }

        print("\n" + "="*50)
        print("📢 DISPATCHING INCIDENT ALERT PAYLOAD:")
        print(json.dumps(alert_payload, indent=2))
        print("="*50 + "\n")

        # If a Slack/Discord webhook URL is provided, dispatch payload
        if self.webhook_url:
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps({"text": json.dumps(alert_payload, indent=2)}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                urllib.request.urlopen(req, timeout=5)
                print("[*] Alert payload sent to ChatOps webhook successfully.")
            except Exception as e:
                print(f"[!] Webhook delivery error: {e}")
