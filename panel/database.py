import uuid
from datetime import datetime

_state = {
    "users": {
        "alice@company.com": {
            "id": "usr_001",
            "email": "alice@company.com",
            "full_name": "Alice Johnson",
            "department": "Engineering",
            "status": "active",
            "password_hash": "hashed_Welcome123",
            "licenses": ["Microsoft 365", "GitHub Enterprise"],
            "created_at": "2024-01-15",
            "last_login": "2025-04-10",
        },
        "bob@company.com": {
            "id": "usr_002",
            "email": "bob@company.com",
            "full_name": "Bob Martinez",
            "department": "Sales",
            "status": "active",
            "password_hash": "hashed_Welcome123",
            "licenses": ["Microsoft 365", "Salesforce"],
            "created_at": "2024-02-20",
            "last_login": "2025-04-12",
        },
        "charlie@company.com": {
            "id": "usr_003",
            "email": "charlie@company.com",
            "full_name": "Charlie Kim",
            "department": "HR",
            "status": "suspended",
            "password_hash": "hashed_Welcome123",
            "licenses": ["Microsoft 365"],
            "created_at": "2024-03-01",
            "last_login": "2025-03-28",
        },
    },
    "available_licenses": [
        "Microsoft 365",
        "GitHub Enterprise",
        "Salesforce",
        "Slack Pro",
        "Zoom Business",
        "Adobe Creative Cloud",
        "Jira Software",
    ],
    "audit_log": [],
}

def get_state():
    return _state

def log_action(action: str, detail: str, actor: str = "IT Agent"):
    _state["audit_log"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "actor": actor,
        "detail": detail,
    })