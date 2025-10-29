import pytest
from unittest.mock import patch

import examples.form as fm
import examples.form_filler as ff


@pytest.fixture
def sample_form():
    """Fixture that returns a small, predictable form description."""
    return [{fm.FLD_NM: "test", ff.PARAM_TYPE: ff.QUERY_STR, ff.QSTN: "Why?"}]


def test_fixture_used(sample_form):
    # ensure the fixture returns the shape we expect
    assert isinstance(sample_form, list)
    assert sample_form[0][fm.FLD_NM] == "test"


def test_raises_value_error():
    # use pytest.raises as a context manager to assert an exception
    with pytest.raises(ValueError):
        int("not-an-int")


@pytest.mark.skip(reason="Demonstration skip - not required in CI")
def test_skipped_example():
    # this test will be skipped
    assert False


def test_patch_get_form(sample_form):
    # patch the get_form function in examples.form to return our fixture
    with patch("examples.form.get_form", return_value=sample_form) as mock_get:
        got = fm.get_form()
        assert got == sample_form
        mock_get.assert_called_once()
