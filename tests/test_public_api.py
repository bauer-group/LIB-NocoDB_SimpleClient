"""Tests for the package's public import surface.

These guard the top-level API contract that the README and examples rely on:
symbols documented as ``from nocodb_simple_client import X`` must actually be
importable, and everything advertised in ``__all__`` must resolve (so
``from nocodb_simple_client import *`` cannot raise).
"""

import importlib

import nocodb_simple_client as nsc


def test_config_symbols_importable_from_top_level():
    """README + examples use `from nocodb_simple_client import NocoDBConfig`."""
    from nocodb_simple_client import NocoDBConfig, load_config

    assert NocoDBConfig.__name__ == "NocoDBConfig"
    assert callable(load_config)
    # same object as the submodule definition (true re-export, not a shadow)
    from nocodb_simple_client.config import NocoDBConfig as CfgFromModule

    assert NocoDBConfig is CfgFromModule


def test_all_entries_resolve():
    """Every name in __all__ must be a real attribute of the package.

    Guards against phantom __all__ entries, which make
    `from nocodb_simple_client import *` raise AttributeError.
    """
    missing = [name for name in nsc.__all__ if not hasattr(nsc, name)]
    assert not missing, f"__all__ lists names not importable from the package: {missing}"


def test_all_has_no_duplicates():
    """__all__ must not list the same name twice.

    The 1.3.5 automated release once appended a duplicate block to __all__;
    this guards against that recurring.
    """
    import collections

    dupes = [name for name, count in collections.Counter(nsc.__all__).items() if count > 1]
    assert not dupes, f"__all__ contains duplicate entries: {dupes}"


def test_star_import_does_not_raise():
    """`from nocodb_simple_client import *` must succeed."""
    ns: dict = {}
    exec("from nocodb_simple_client import *", ns)  # noqa: S102 - intentional
    assert "NocoDBConfig" in ns
    assert "NocoDBClient" in ns


def test_documented_core_symbols_present():
    """A representative slice of the documented public API is importable."""
    for name in (
        "NocoDBClient",
        "NocoDBTable",
        "NocoDBMetaClient",
        "NocoDBConfig",
        "load_config",
        "QueryBuilder",
        "FilterBuilder",
        "SortBuilder",
        "NocoDBException",
    ):
        assert hasattr(nsc, name), f"{name} missing from public API"


def test_examples_use_importable_symbols():
    """Static guard: every `from nocodb_simple_client import ...` in examples/
    resolves. This is the check that would have caught the NocoDBConfig gap."""
    import ast
    import glob
    import os

    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    failures = []
    for path in sorted(glob.glob(os.path.join(examples_dir, "*.py"))):
        tree = ast.parse(open(path, encoding="utf-8").read(), path)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("nocodb_simple_client")
            ):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    if alias.name != "*" and not hasattr(module, alias.name):
                        failures.append(f"{os.path.basename(path)}: {node.module}.{alias.name}")
    assert not failures, f"examples import unresolvable symbols: {failures}"
