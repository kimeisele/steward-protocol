"""Tests for F811 redefinition remedy."""

from pathlib import Path

from vibe_core.protocols.shuddhi import ShuddhiStatus
from vibe_core.shuddhi.engine import ShuddhiEngine


def _purify(tmp_path: Path, source: str):
    target = tmp_path / "f811_case.py"
    target.write_text(source)
    engine = ShuddhiEngine()
    return engine.purify(target, "F811")


def test_removes_duplicate_alias_in_same_import_from(tmp_path: Path):
    result = _purify(
        tmp_path,
        "from typing import List, List, Dict\n",
    )
    assert result.status == ShuddhiStatus.PURIFIED
    assert result.purified_code == "from typing import List, Dict\n"


def test_removes_later_duplicate_import_from_same_source(tmp_path: Path):
    result = _purify(
        tmp_path,
        "from typing import Any\nfrom typing import Any\n",
    )
    assert result.status == ShuddhiStatus.PURIFIED
    assert result.purified_code == "from typing import Any\n"


def test_removes_later_duplicate_plain_import(tmp_path: Path):
    result = _purify(
        tmp_path,
        "import json\nimport json\n",
    )
    assert result.status == ShuddhiStatus.PURIFIED
    assert result.purified_code == "import json\n"


def test_skips_same_alias_from_different_sources_for_safety(tmp_path: Path):
    result = _purify(
        tmp_path,
        "from pathlib import Path as P\nfrom typing import Any as P\n",
    )
    assert result.status == ShuddhiStatus.SKIPPED
