import pytest
import tempfile
from pathlib import Path
from snk import Nest

@pytest.fixture()
def bin_dir(tmpdir: Path):
    return Path(tmpdir) / 'bin'

@pytest.fixture()
def snk_home(tmpdir: Path):
    return Path(tmpdir) / 'snk'

@pytest.fixture()
def nest(snk_home, bin_dir):
    return Nest(snk_home, bin_dir)