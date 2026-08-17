import subprocess

class ActionRemediator:
    def __init__(self, ingress_name="netflex-smart-gateway", namespace="netflex-origin"):
        self.ingress_name = ingress_name
        self.namespace = namespace

    def get_current_denylist(self):
        """Fetches the current denylist from the active Ingress annotation."""
        cmd = [
            "kubectl", "get", "ingress", self.ingress_name,
            "-n", self.namespace,
            "-o", "jsonpath={.metadata.annotations.nginx\\.ingress\\.kubernetes\\.io/denylist-source-range}"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        current = result.stdout.strip()
        if not current:
            return []
        return [ip.strip() for ip in current.split(",") if ip.strip()]

    def block_ip(self, ip_to_block: str, reason: str = "AIOps Automated Threat Mitigation"):
        """Appends the malicious IP to the Ingress denylist annotation."""
        if not ip_to_block or ip_to_block == "-":
            return False

        current_list = self.get_current_denylist()
        if ip_to_block in current_list:
            print(f"[*] IP {ip_to_block} is already in the blocklist.")
            return True

        current_list.append(ip_to_block)
        new_denylist = ",".join(current_list)

        cmd = [
            "kubectl", "annotate", "ingress", self.ingress_name,
            "-n", self.namespace,
            f"nginx.ingress.kubernetes.io/denylist-source-range={new_denylist}",
            "--overwrite"
        ]

        print(f"\n[🚨 REMEDIATION TRIGGERED]")
        print(f" -> Threat: {reason}")
        print(f" -> Action: Pushing dynamic NGINX block rule for IP: {ip_to_block}")

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f" -> [SUCCESS] NGINX Ingress firewall updated in namespace '{self.namespace}'.")
            return True
        else:
            print(f" -> [ERROR] Failed to annotate Ingress: {result.stderr}")
            return False
