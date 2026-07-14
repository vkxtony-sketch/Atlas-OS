"""Atlas OS - Security Team."""
from __future__ import annotations

from core.teams.base import Team


class SecurityTeam(Team):
    name = "security"
    description = "Threat analysis, dependency review, authentication review, secrets."
    responsibilities = ["Find vulnerabilities", "Stop secrets leaking", "Review authz"]
    review_focus = [
        "auth", "password", "secret", "token", "permission", "cve",
        "vuln", "vulnerability", "security", "crypt", "rsa", "tls",
        "injection", "xss", "csrf", "ssrf",
    ]
    members = ["security_reviewer"]
