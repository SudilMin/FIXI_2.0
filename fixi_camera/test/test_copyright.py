# Copyright 2026 sudil-minthaka

from ament_copyright.main import main
import pytest


@pytest.mark.copyright
@pytest.mark.linter
def test_copyright() -> None:
    """Run the ROS 2 copyright linter."""
    rc = main(argv=[".", "test"])
    assert rc == 0, "Found copyright errors"
