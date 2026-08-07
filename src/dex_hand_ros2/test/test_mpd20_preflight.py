import pytest

from dex_hand_ros2.mpd20_preflight import _expanded, _int_list, build_parser


def test_preflight_list_parsing_and_expansion():
    assert _int_list("1, 2,3") == [1, 2, 3]
    assert _expanded([120], 3, "limits") == [120, 120, 120]
    assert _expanded([1, -1], 2, "directions") == [1, -1]
    with pytest.raises(ValueError, match="must contain"):
        _expanded([1, 2], 3, "limits")


def test_preflight_requires_port():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])
