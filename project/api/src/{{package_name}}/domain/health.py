from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthReport:
    """Liveness snapshot returned by the health check."""

    status: str


def check_health() -> HealthReport:
    """Report service liveness. Pure domain logic, no I/O."""
    return HealthReport(status="ok")
