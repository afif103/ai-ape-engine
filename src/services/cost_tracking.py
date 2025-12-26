"""AWS cost tracking and estimation service."""

import time
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class AWSCostEstimate:
    """AWS service cost estimate."""

    service: str
    operation: str
    units: float
    cost_per_unit: float
    total_cost: float
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "operation": self.operation,
            "units": self.units,
            "cost_per_unit": self.cost_per_unit,
            "total_cost": round(self.total_cost, 4),
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


class CostTracker:
    """Tracks AWS usage costs and provides estimates."""

    # AWS Pricing (as of 2024, subject to change)
    PRICING = {
        "textract": {
            "detect_document_text": {"per_page": 0.0015},  # $0.0015 per page
            "analyze_document": {"per_page": 0.005},  # $0.005 per page (tables/forms)
        },
        "comprehend": {
            "detect_entities": {"per_unit": 0.0001},  # $0.0001 per unit
            "detect_key_phrases": {"per_unit": 0.0001},  # $0.0001 per unit
            "detect_sentiment": {"per_unit": 0.0001},  # $0.0001 per unit
        },
        "glue": {
            "catalog": {"per_hour": 0.44}  # $0.44 per DPU hour (simplified)
        },
        "athena": {
            "query": {"per_tb": 5.00}  # $5.00 per TB scanned
        },
        "s3": {
            "storage": {"per_gb_month": 0.023},  # $0.023 per GB/month
            "requests": {"per_1000": 0.005},  # $0.005 per 1,000 requests
        },
    }

    def __init__(self):
        self.usage_history: List[AWSCostEstimate] = []
        self.session_start = time.time()

    def estimate_textract_cost(self, operation: str, pages: int = 1) -> float:
        """Estimate Textract cost."""
        if operation not in self.PRICING["textract"]:
            return 0.0

        cost_per_page = self.PRICING["textract"][operation]["per_page"]
        total_cost = pages * cost_per_page

        self._record_usage("textract", operation, pages, cost_per_page, total_cost)
        return total_cost

    def estimate_comprehend_cost(self, operations: List[str], text_length: int) -> float:
        """Estimate Comprehend cost based on text length."""
        # Comprehend pricing is per "unit" (100 characters)
        units = max(1, text_length / 100)  # Minimum 1 unit
        cost_per_unit = self.PRICING["comprehend"]["detect_entities"]["per_unit"]

        total_cost = 0
        for operation in operations:
            if operation in self.PRICING["comprehend"]:
                op_cost = units * self.PRICING["comprehend"][operation]["per_unit"]
                total_cost += op_cost
                self._record_usage(
                    "comprehend",
                    operation,
                    units,
                    self.PRICING["comprehend"][operation]["per_unit"],
                    op_cost,
                )

        return total_cost

    def estimate_s3_cost(self, storage_gb: float = 0, requests: int = 0) -> float:
        """Estimate S3 costs."""
        storage_cost = (
            storage_gb * self.PRICING["s3"]["storage"]["per_gb_month"] / 30
        )  # Daily estimate
        request_cost = (requests / 1000) * self.PRICING["s3"]["requests"]["per_1000"]

        total_cost = storage_cost + request_cost

        if storage_cost > 0:
            self._record_usage(
                "s3",
                "storage",
                storage_gb,
                self.PRICING["s3"]["storage"]["per_gb_month"] / 30,
                storage_cost,
            )
        if request_cost > 0:
            self._record_usage(
                "s3",
                "requests",
                requests / 1000,
                self.PRICING["s3"]["requests"]["per_1000"],
                request_cost,
            )

        return total_cost

    def _record_usage(
        self, service: str, operation: str, units: float, cost_per_unit: float, total_cost: float
    ):
        """Record usage for cost tracking."""
        estimate = AWSCostEstimate(
            service=service,
            operation=operation,
            units=units,
            cost_per_unit=cost_per_unit,
            total_cost=total_cost,
            timestamp=time.time(),
        )
        self.usage_history.append(estimate)

        # Keep only last 1000 records
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]

    def get_session_costs(self) -> Dict[str, Any]:
        """Get cost summary for current session."""
        total_cost = sum(estimate.total_cost for estimate in self.usage_history)

        service_breakdown = {}
        for estimate in self.usage_history:
            if estimate.service not in service_breakdown:
                service_breakdown[estimate.service] = 0
            service_breakdown[estimate.service] += estimate.total_cost

        return {
            "total_cost": round(total_cost, 4),
            "service_breakdown": {k: round(v, 4) for k, v in service_breakdown.items()},
            "usage_count": len(self.usage_history),
            "session_duration": time.time() - self.session_start,
            "estimates": [est.to_dict() for est in self.usage_history[-10:]],  # Last 10
        }

    def get_monthly_estimate(self) -> Dict[str, Any]:
        """Estimate monthly costs based on current usage patterns."""
        if not self.usage_history:
            return {"monthly_estimate": 0, "note": "No usage data available"}

        # Simple extrapolation - assumes current usage rate continues
        session_duration_hours = (time.time() - self.session_start) / 3600
        if session_duration_hours < 1:
            return {"monthly_estimate": 0, "note": "Session too short for estimate"}

        session_cost = sum(est.total_cost for est in self.usage_history)
        hourly_rate = session_cost / session_duration_hours
        monthly_estimate = hourly_rate * 24 * 30  # 24 hours * 30 days

        return {
            "monthly_estimate": round(monthly_estimate, 2),
            "hourly_rate": round(hourly_rate, 4),
            "based_on_hours": round(session_duration_hours, 2),
            "note": "Estimate based on current session usage patterns",
        }


# Global cost tracker instance
cost_tracker = CostTracker()
