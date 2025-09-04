import json
from typing import Any, Dict, List

from flask import current_app


class ContractManagerService:
    """Service for managing contract manager names in Redis"""

    REDIS_KEY = "contract-managers"

    def __init__(self):
        self.redis = current_app.config["SESSION_REDIS"]

    def get_all(self) -> List[str]:
        """Get all contract manager names in alphabetical order"""
        data = self.redis.get(self.REDIS_KEY)
        if data:
            managers = json.loads(data.decode("utf-8"))
            return sorted(managers, key=str.lower)  # Case-insensitive alphabetical sort
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

    def get_paginated(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get paginated contract manager names

        Args:
            page: Page number (1-based)
            per_page: Number of items per page

        Returns:
            Dictionary containing:
            - managers: List of managers for the current page
            - total_count: Total number of managers
            - page: Current page number
            - per_page: Items per page
            - has_next: Whether there is a next page
            - has_prev: Whether there is a previous page
        """
        all_managers = self.get_all()
        total_count = len(all_managers)

        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        managers = all_managers[start_idx:end_idx]

        return {
            "managers": managers,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "has_next": end_idx < total_count,
            "has_prev": page > 1,
        }

    def clear_all(self) -> None:
        """Clear all contract managers"""
        self.redis.delete(self.REDIS_KEY)
