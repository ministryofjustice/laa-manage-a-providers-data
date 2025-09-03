import json
from typing import List

from flask import current_app


class ContractManagerService:
    """Service for managing contract manager names in Redis"""

    REDIS_KEY = "contract_managers"

    def __init__(self):
        self.redis = current_app.config["SESSION_REDIS"]

    def get_all(self) -> List[str]:
        """Get all contract manager names"""
        data = self.redis.get(self.REDIS_KEY)
        if data:
            return json.loads(data.decode("utf-8"))
        return []

    def add(self, name: str) -> bool:
        """Add a new contract manager name"""
        if not name or not name.strip():
            return False

        managers = self.get_all()
        name = name.strip()

        if name not in managers:
            managers.append(name)
            self.redis.set(self.REDIS_KEY, json.dumps(managers))
            return True
        return False

    def remove(self, name: str) -> bool:
        """Remove a contract manager name"""
        managers = self.get_all()
        if name in managers:
            managers.remove(name)
            self.redis.set(self.REDIS_KEY, json.dumps(managers))
            return True
        return False

    def clear_all(self) -> None:
        """Clear all contract managers"""
        self.redis.delete(self.REDIS_KEY)
