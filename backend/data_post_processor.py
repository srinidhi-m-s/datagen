"""
Post-processing utilities to improve generated data consistency.
"""

from typing import Any, Dict, List


class DataPostProcessor:
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []

        cleaned = [self._normalize_row(row) for row in data if isinstance(row, dict)]
        if not cleaned:
            return []

        self._enforce_unique_id_like_fields(cleaned)
        self._enforce_unique_email(cleaned)
        return cleaned

    def _normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        for k, v in row.items():
            key = str(k).strip()
            if isinstance(v, str):
                normalized[key] = v.strip()
            else:
                normalized[key] = v
        return normalized

    def _enforce_unique_id_like_fields(self, data: List[Dict[str, Any]]) -> None:
        if not data:
            return

        headers = list(data[0].keys())
        id_fields = [h for h in headers if "id" in h.lower()]

        for field in id_fields:
            seen = set()
            next_id = 1
            for row in data:
                value = row.get(field)
                if value in seen or value is None or value == "":
                    while next_id in seen:
                        next_id += 1
                    row[field] = next_id
                    seen.add(next_id)
                else:
                    seen.add(value)

    def _enforce_unique_email(self, data: List[Dict[str, Any]]) -> None:
        if not data:
            return

        email_field = None
        for header in data[0].keys():
            if "email" in header.lower():
                email_field = header
                break

        if not email_field:
            return

        seen = {}
        for row in data:
            email = row.get(email_field)
            if not isinstance(email, str) or "@" not in email:
                continue

            lowered = email.lower()
            count = seen.get(lowered, 0)
            if count > 0:
                local, domain = email.split("@", 1)
                row[email_field] = f"{local}+{count}@{domain}"
            seen[lowered] = count + 1


data_post_processor = DataPostProcessor()
