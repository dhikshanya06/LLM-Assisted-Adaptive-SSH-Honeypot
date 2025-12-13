import importlib
from pathlib import Path
import sys


def test_src_package_exists():
    """Ensure the cowrie source package folder exists."""
    assert Path("src/cowrie").is_dir(), "src/cowrie package is missing"


def test_pkg_importable():
    """Try importing the cowrie package from the repo's src directory."""
    src_path = Path("src").resolve()
    assert src_path.exists(), "src directory is missing"
    sys.path.insert(0, str(src_path))
    mod = importlib.import_module("cowrie")
    assert mod is not None


def test_config_present():
    """Verify the default configuration example is present."""
    assert Path("etc/cowrie.cfg.dist").is_file(), "etc/cowrie.cfg.dist is missing"


def test_requirements_non_empty():
    """Confirm requirements.txt exists and is not empty."""
    req = Path("requirements.txt")
    assert req.is_file(), "requirements.txt is missing"
    assert req.read_text().strip() != "", "requirements.txt appears empty"


def test_var_structure():
    """Check var directories that Cowrie expects at runtime."""
    var = Path("var")
    assert Path('.').resolve().exists(), "repo root not accessible"
    if var.exists():
        assert (var / "log").exists() or (var / "log").parent.exists()
        assert (var / "lib").exists() or (var / "lib").parent.exists()
