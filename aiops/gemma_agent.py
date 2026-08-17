import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

def analyze_log_entry(log_entry: dict, ollama_endpoint: str = OLLAMA_URL) -> dict:
    """
    Sends raw edge gateway log telemetry to Gemma-2B to classify the threat level.
    """
    prompt = f"""
    You are an automated AIOps Security Analyst for an Edge CDN Gateway.
    Analyze the following HTTP telemetry log and determine if it represents a malicious Bot/Attacker or a Legitimate User.

    Log Entry:
    {json.dumps(log_entry, indent=2)}

    Respond ONLY with valid JSON in this exact structure:
    {{
      "is_threat": true,
      "threat_type": "BOT_CREDENTIAL_STUFFING" | "HONEYPOT_HIT" | "RATE_LIMIT_ABUSE" | "NONE",
      "confidence": 0.95,
      "recommended_action": "BLOCK_IP" | "RATE_LIMIT" | "ALLOW",
      "reasoning": "Brief explanation"
    }}
    """
    
    payload = {
        "model": "gemma2:2b",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    
    req = urllib.request.Request(
        ollama_endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return json.loads(result["response"])
    except Exception as e:
        return {
            "is_threat": False,
            "error": str(e),
            "threat_type": "UNKNOWN",
            "recommended_action": "ALLOW"
        }
