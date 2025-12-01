"""Configuration management for home-display-agent."""

import os
from dataclasses import dataclass, field


@dataclass
class ServiceConfig:
    """Configuration for external service endpoints."""

    audio_id_url: str = field(
        default_factory=lambda: os.getenv("AUDIO_ID_URL", "http://audio-id:8000")
    )
    image_opt_url: str = field(
        default_factory=lambda: os.getenv("IMAGE_OPT_URL", "http://image-opt:8000")
    )
    overlay_url: str = field(
        default_factory=lambda: os.getenv("OVERLAY_URL", "http://overlay:8000")
    )
    dispatcher_url: str = field(
        default_factory=lambda: os.getenv("DISPATCHER_URL", "http://dispatcher:8000")
    )
    monitor_url: str = field(
        default_factory=lambda: os.getenv("MONITOR_URL", "http://monitor:8000")
    )


@dataclass
class RabbitMQConfig:
    """Configuration for RabbitMQ connection."""

    host: str = field(default_factory=lambda: os.getenv("RABBITMQ_HOST", "rabbitmq"))
    port: int = field(
        default_factory=lambda: int(os.getenv("RABBITMQ_PORT", "5672"))
    )
    user: str = field(default_factory=lambda: os.getenv("RABBITMQ_USER", "guest"))
    password: str = field(
        default_factory=lambda: os.getenv("RABBITMQ_PASSWORD", "guest")
    )

    @property
    def url(self) -> str:
        """Return AMQP connection URL."""
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


@dataclass
class SambaConfig:
    """Configuration for Samba share."""

    host: str = field(default_factory=lambda: os.getenv("SAMBA_HOST", "samba"))
    share: str = field(default_factory=lambda: os.getenv("SAMBA_SHARE", "media"))
    user: str = field(default_factory=lambda: os.getenv("SAMBA_USER", "guest"))
    password: str = field(default_factory=lambda: os.getenv("SAMBA_PASSWORD", ""))


@dataclass
class Config:
    """Main configuration for home-display-agent."""

    services: ServiceConfig = field(default_factory=ServiceConfig)
    rabbitmq: RabbitMQConfig = field(default_factory=RabbitMQConfig)
    samba: SambaConfig = field(default_factory=SambaConfig)
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config()
