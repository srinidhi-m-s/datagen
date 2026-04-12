"""
Performance tracking and comparison utilities for generation modes.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
import time
from typing import Any, Dict, List, Optional


@dataclass
class GenerationMetrics:
    mode: str
    query: str
    response_time_ms: float
    record_count: int
    schema_compliance: float
    relationship_score: float
    data_quality_score: float
    overall_score: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PerformanceComparator:
    def __init__(self):
        self._history: List[GenerationMetrics] = []

    def start_timer(self) -> float:
        return time.perf_counter()

    def stop_timer(self, start_time: float) -> float:
        return (time.perf_counter() - start_time) * 1000.0

    def _schema_compliance(self, data: List[Dict[str, Any]], expected_schema: Dict[str, str]) -> float:
        if not data or not expected_schema:
            return 0.0

        expected_keys = set(expected_schema.keys())
        if not expected_keys:
            return 0.0

        per_row = []
        for row in data:
            row_keys = set(row.keys())
            matches = len(expected_keys.intersection(row_keys))
            per_row.append((matches / len(expected_keys)) * 100)

        return round(statistics.mean(per_row), 2)

    def _relationship_score(self, data: List[Dict[str, Any]], relationships: Optional[List[Dict[str, Any]]]) -> float:
        if not data:
            return 0.0
        if not relationships:
            return 80.0

        score = 100.0
        lower_headers = {k.lower(): k for k in data[0].keys()} if data else {}

        for rel in relationships:
            if rel.get("type") == "uniqueness":
                field = rel.get("field")
                if not field:
                    continue
                values = [row.get(field) for row in data]
                if len(values) != len(set(values)):
                    score -= 10.0
            if rel.get("type") == "email_name_match":
                name_key = lower_headers.get(rel.get("name_field", "name").lower())
                email_key = lower_headers.get(rel.get("email_field", "email").lower())
                if name_key and email_key:
                    mismatch = 0
                    for row in data:
                        name = str(row.get(name_key, "")).lower().replace(" ", ".")
                        email = str(row.get(email_key, "")).lower()
                        if name and name.split(".")[0] not in email:
                            mismatch += 1
                    score -= (mismatch / max(1, len(data))) * 20.0

        return max(0.0, round(score, 2))

    def _quality_score(self, data: List[Dict[str, Any]], unique_fields: Optional[List[str]]) -> float:
        if not data:
            return 0.0

        completeness = 0.0
        uniqueness = 100.0

        total_values = 0
        empty_values = 0
        for row in data:
            for value in row.values():
                total_values += 1
                if value is None or (isinstance(value, str) and not value.strip()):
                    empty_values += 1

        if total_values > 0:
            completeness = (1 - (empty_values / total_values)) * 100

        if unique_fields:
            for field in unique_fields:
                values = [row.get(field) for row in data]
                if len(values) != len(set(values)):
                    uniqueness -= 20

        return max(0.0, round((completeness * 0.7) + (uniqueness * 0.3), 2))

    def record_metrics(
        self,
        mode: str,
        query: str,
        response_time_ms: float,
        data: List[Dict[str, Any]],
        expected_schema: Dict[str, str],
        relationships: Optional[List[Dict[str, Any]]] = None,
        unique_fields: Optional[List[str]] = None,
    ) -> GenerationMetrics:
        schema_score = self._schema_compliance(data, expected_schema)
        rel_score = self._relationship_score(data, relationships)
        quality_score = self._quality_score(data, unique_fields)
        overall = round((schema_score * 0.4) + (rel_score * 0.3) + (quality_score * 0.3), 2)

        metrics = GenerationMetrics(
            mode=mode,
            query=query,
            response_time_ms=round(response_time_ms, 2),
            record_count=len(data) if data else 0,
            schema_compliance=schema_score,
            relationship_score=rel_score,
            data_quality_score=quality_score,
            overall_score=overall,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        self._history.append(metrics)
        return metrics

    def compare_modes(self, normal_metrics: GenerationMetrics, enhanced_metrics: GenerationMetrics) -> Dict[str, Any]:
        def pct_delta(new_val: float, old_val: float) -> float:
            if old_val == 0:
                return 0.0
            return round(((new_val - old_val) / old_val) * 100, 2)

        improvements = {
            "response_time": {
                "improvement_percent": pct_delta(normal_metrics.response_time_ms, enhanced_metrics.response_time_ms) * -1
            },
            "schema_compliance": {
                "improvement_percent": pct_delta(enhanced_metrics.schema_compliance, normal_metrics.schema_compliance)
            },
            "relationship_score": {
                "improvement_percent": pct_delta(enhanced_metrics.relationship_score, normal_metrics.relationship_score)
            },
            "data_quality": {
                "improvement_percent": pct_delta(enhanced_metrics.data_quality_score, normal_metrics.data_quality_score)
            },
            "overall": {
                "improvement_percent": pct_delta(enhanced_metrics.overall_score, normal_metrics.overall_score)
            },
        }

        benefits = []
        if improvements["schema_compliance"]["improvement_percent"] > 0:
            benefits.append("Better schema compliance")
        if improvements["relationship_score"]["improvement_percent"] > 0:
            benefits.append("Improved semantic consistency")
        if improvements["data_quality"]["improvement_percent"] > 0:
            benefits.append("Higher data quality")
        if not benefits:
            benefits.append("Comparable quality with current prompt")

        return {
            "normal_mode": normal_metrics.to_dict(),
            "enhanced_mode": enhanced_metrics.to_dict(),
            "improvements": improvements,
            "summary": {
                "key_benefits": benefits
            },
        }

    def get_statistics(self) -> Dict[str, Any]:
        if not self._history:
            return {
                "total_runs": 0,
                "normal_runs": 0,
                "enhanced_runs": 0,
                "avg_response_time_ms": 0.0,
                "avg_overall_score": 0.0,
            }

        response_times = [m.response_time_ms for m in self._history]
        overall_scores = [m.overall_score for m in self._history]

        return {
            "total_runs": len(self._history),
            "normal_runs": len([m for m in self._history if m.mode == "normal"]),
            "enhanced_runs": len([m for m in self._history if m.mode == "enhanced"]),
            "avg_response_time_ms": round(statistics.mean(response_times), 2),
            "avg_overall_score": round(statistics.mean(overall_scores), 2),
            "latest": self._history[-1].to_dict(),
        }


performance_comparator = PerformanceComparator()
