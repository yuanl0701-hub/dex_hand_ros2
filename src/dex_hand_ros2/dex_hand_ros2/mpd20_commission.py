"""Compatibility entry point for bounded MPD20 commissioning."""

from .commissioning.mpd20_commission import *  # noqa: F403
from .commissioning.mpd20_commission import main

__all__ = ["main"]
