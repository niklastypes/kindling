import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Process configuration, read once from the environment."""

    cors_allowed_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
        return cls(cors_allowed_origins=tuple(o for o in raw.split(",") if o))
