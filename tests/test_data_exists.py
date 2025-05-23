"""Test that the package data exists in the correct places."""

import pytest

from py21cmfast import DATA_PATH


@pytest.fixture(scope="module")
def datafiles():
    return list(DATA_PATH.glob("*.dat"))


def test_exists(datafiles):
    for fl in datafiles:
        assert fl.exists()

    assert (DATA_PATH / "x_int_tables").exists()
    assert (DATA_PATH / "x_int_tables").is_dir()


def test_readable(datafiles):
    for fname in datafiles:
        with fname.open() as fl:
            assert len(fl.read()) > 0
