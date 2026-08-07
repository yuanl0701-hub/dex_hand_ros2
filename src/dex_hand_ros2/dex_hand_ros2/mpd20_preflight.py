"""Compatibility entry point for MPD20 preflight."""

from .commissioning.mpd20_preflight import (
    _expanded,
    _int_list,
    build_parser,
    main,
    run_preflight,
)

__all__ = ["_expanded", "_int_list", "build_parser", "main", "run_preflight"]
