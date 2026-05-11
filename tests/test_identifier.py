import pytest

from identifier import Id, SubId


@pytest.fixture(autouse=True)
def reset_subid_counters():
    SubId._last_id_by_level = {
        SubId.Level.ONE: 0,
        SubId.Level.TWO: 0,
    }


def test_id_rejects_non_positive_values():
    with pytest.raises(ValueError, match="Not a positive integer value"):
        Id(0)

    with pytest.raises(ValueError, match="Not a positive integer value"):
        Id(-1)


def test_id_rejects_values_that_do_not_fit_in_configured_bytes():
    with pytest.raises(ValueError, match="Exceeds max value"):
        Id(256**2, num_bytes=2)


def test_id_serializes_to_big_endian_bytes_and_hex():
    identifier = Id(258, num_bytes=2)

    assert identifier.to_bytes() == b"\x01\x02"
    assert identifier.to_hex() == "0102"
    assert str(identifier) == "258"
    assert repr(identifier) == "Id(258)"


def test_subid_uses_parent_bytes_and_level_one_counter():
    parent = Id(7)
    first = SubId(parent)
    second = SubId(parent)

    assert first.level is SubId.Level.ONE
    assert first.val == 1
    assert first.to_bytes() == b"\x00\x07\x00\x01"
    assert str(first) == "(7, 1)"
    assert repr(first) == "SubId(7, 1)"

    assert second.level is SubId.Level.ONE
    assert second.val == 2
    assert second.to_bytes() == b"\x00\x07\x00\x02"


def test_nested_subid_uses_parent_chain_and_level_two_counter():
    parent = Id(7)
    child = SubId(parent)
    grandchild = SubId(child)
    another_grandchild = SubId(child)

    assert grandchild.level is SubId.Level.TWO
    assert grandchild.val == 1
    assert grandchild.to_bytes() == b"\x00\x07\x00\x01\x00\x00\x00\x01"
    assert str(grandchild) == "(7, 1, 1)"
    assert repr(grandchild) == "SubId(7, 1, 1)"

    assert another_grandchild.level is SubId.Level.TWO
    assert another_grandchild.val == 2
    assert another_grandchild.to_bytes() == b"\x00\x07\x00\x01\x00\x00\x00\x02"


def test_subid_rejects_nesting_beyond_two_levels():
    parent = Id(7)
    child = SubId(parent)
    grandchild = SubId(child)

    with pytest.raises(AssertionError, match="Nesting beyond two sub-levels is not supported"):
        SubId(grandchild)
