"""
Data filtering and validation helpers.
"""

from typing import Any, Dict, List


class DataFilter:
    """Provides lightweight filtering and validation for generated datasets."""

    def filter_data(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not data:
            return []
        if not filters:
            return data

        def matches(row: Dict[str, Any]) -> bool:
            for field, condition in filters.items():
                value = row.get(field)

                # Equality shortcut: {"field": "x"}
                if not isinstance(condition, dict):
                    if value != condition:
                        return False
                    continue

                for op, expected in condition.items():
                    if not self._evaluate(value, op, expected):
                        return False
            return True

        return [row for row in data if matches(row)]

    def _evaluate(self, value: Any, op: str, expected: Any) -> bool:
        if op == "eq":
            return value == expected
        if op == "ne":
            return value != expected
        if op == "gt":
            return value is not None and expected is not None and value > expected
        if op == "lt":
            return value is not None and expected is not None and value < expected
        if op == "gte":
            return value is not None and expected is not None and value >= expected
        if op == "lte":
            return value is not None and expected is not None and value <= expected
        if op == "contains":
            return value is not None and str(expected).lower() in str(value).lower()
        if op == "in":
            return value in expected if isinstance(expected, list) else False
        return False

    def validate_data(self, data: List[Dict[str, Any]], constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        if not data:
            return {
                "total_records": 0,
                "valid_records": 0,
                "quality_score": 0.0,
                "issues": ["No records generated"],
            }

        required_fields = set(data[0].keys())
        valid_records = 0
        issues: List[str] = []

        for idx, row in enumerate(data):
            row_fields = set(row.keys())
            if row_fields != required_fields:
                missing = required_fields - row_fields
                extra = row_fields - required_fields
                if missing:
                    issues.append(f"Row {idx + 1}: missing fields {sorted(missing)}")
                if extra:
                    issues.append(f"Row {idx + 1}: unexpected fields {sorted(extra)}")

            has_empty = any(v is None or (isinstance(v, str) and not v.strip()) for v in row.values())
            if has_empty:
                issues.append(f"Row {idx + 1}: contains empty values")
            else:
                valid_records += 1

        if constraints:
            issues.append("Custom constraints were provided but strict rule checks are not enabled in this lightweight validator")

        quality_score = round((valid_records / len(data)) * 100, 2) if data else 0.0

        return {
            "total_records": len(data),
            "valid_records": valid_records,
            "quality_score": quality_score,
            "issues": issues[:20],
        }


data_filter = DataFilter()
