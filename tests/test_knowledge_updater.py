'''Tests for the knowledge-updater tool.'''
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "knowledge_updater.py"


@pytest.fixture
def fresh_brain(monkeypatch, tmp_path):
    brain = tmp_path / "SECOND-KNOWLEDGE-BRAIN.md"
    brain.write_text("# Knowledge Brain\n\n## Knowledge Update Log\n", encoding="utf-8")
    monkeypatch.setenv("ECO_BRAIN_PATH", str(brain))
    return brain


def test_seed_appends_at_least_ten_entries(fresh_brain):
    subprocess.run(
        [sys.executable, str(TOOL), "--seed"],
        check=True,
        cwd=str(ROOT),
    )
    text = fresh_brain.read_text(encoding="utf-8")
    hashes = re.findall(r"<!--h:([0-9a-f]{12})-->", text)
    assert len(hashes) >= 10
    # Verify the dated log entry exists.
    assert "Auto-crawl appended" in text


def test_seed_dedup_on_second_run(fresh_brain):
    subprocess.run([sys.executable, str(TOOL), "--seed"], check=True, cwd=str(ROOT))
    text1 = fresh_brain.read_text(encoding="utf-8")
    hashes1 = set(re.findall(r"<!--h:([0-9a-f]{12})-->", text1))

    subprocess.run([sys.executable, str(TOOL), "--seed"], check=True, cwd=str(ROOT))
    text2 = fresh_brain.read_text(encoding="utf-8")
    hashes2 = set(re.findall(r"<!--h:([0-9a-f]{12})-->", text2))

    assert hashes1 == hashes2


def test_dry_run_does_not_write(fresh_brain):
    before = fresh_brain.read_text(encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(TOOL), "--seed", "--dry-run"],
        check=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    after = fresh_brain.read_text(encoding="utf-8")
    assert after == before
    assert "would append" in result.stdout.lower()
