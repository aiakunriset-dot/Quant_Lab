from hypothesis import given, strategies as st


@given(st.integers(min_value=1, max_value=10_000))
def test_positive_integer_property(value: int) -> None:
    """Verify the property-test harness is operational."""
    assert value > 0
