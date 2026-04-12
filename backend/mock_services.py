"""
Mock/bridge services for optional Kaggle and RAG context.
"""

from typing import Any, Dict

from backend.rag_service import rag_service


def _guess_domain(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["agriculture", "irrigation", "farm", "crop", "soil"]):
        return "agriculture"
    if any(k in q for k in ["employee", "hr", "salary", "department"]):
        return "hr"
    if any(k in q for k in ["product", "order", "customer", "ecommerce"]):
        return "ecommerce"
    if any(k in q for k in ["transaction", "payment", "bank", "finance"]):
        return "finance"
    return "general"


class MockKaggleService:
    async def search_datasets(self, query: str) -> Dict[str, Any]:
        domain = _guess_domain(query)

        schemas = {
            "agriculture": {
                "farm_id": "int",
                "field_id": "int",
                "soil_moisture": "float",
                "irrigation_status": "string",
                "water_flow_lpm": "float",
                "temperature_c": "float",
                "humidity_pct": "float",
                "timestamp": "date",
            },
            "hr": {
                "employee_id": "int",
                "name": "string",
                "email": "string",
                "department": "string",
                "salary": "float",
                "hire_date": "date",
            },
            "ecommerce": {
                "order_id": "int",
                "customer_id": "int",
                "product_name": "string",
                "quantity": "int",
                "unit_price": "float",
                "order_date": "date",
            },
        }

        samples = {
            "agriculture": [
                {
                    "farm_id": 101,
                    "field_id": 12,
                    "soil_moisture": 34.2,
                    "irrigation_status": "on",
                    "water_flow_lpm": 18.6,
                    "temperature_c": 29.4,
                    "humidity_pct": 62.0,
                    "timestamp": "2026-04-09",
                }
            ]
        }

        return {
            "provider": "mock-kaggle",
            "query": query,
            "domain": domain,
            "schema": schemas.get(domain, {"id": "int", "name": "string", "value": "string"}),
            "samples": samples.get(domain, []),
            "patterns": [
                "Keep identifiers unique",
                "Use realistic value ranges",
                "Prefer consistent units across numeric fields",
            ],
        }


class MockRAGService:
    async def get_context(self, query: str) -> Dict[str, Any]:
        return await rag_service.retrieve_context(query, top_k=4)


mock_kaggle_service = MockKaggleService()
mock_rag_service = MockRAGService()
