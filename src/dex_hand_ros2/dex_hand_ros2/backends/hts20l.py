"""HTS-20L adapter isolated from the MPD20 backend selection."""

from .mpd20 import MPD20Driver


class HTS20LDriver(MPD20Driver):
    """HTS-20L position adapter with blocked persistent baud writes.

    The recovered repository does not contain an authoritative baud-code table,
    so a guessed persistent setting is deliberately not exposed.
    """

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        del target_id, new_baud
        raise NotImplementedError(
            "HTS-20L baud mapping is blocked pending authoritative documentation"
        )
