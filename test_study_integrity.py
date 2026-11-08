"""Frozen inputs must be verified before a study run can build or call anything."""

import shutil
import sys
from pathlib import Path

import pytest

import run_experiment

ROOT = Path(__file__).resolve().parent


def frozen_copy(tmp_path):
    manifest = ROOT / "DIGESTS.sha256"
    shutil.copyfile(manifest, tmp_path / manifest.name)
    for line in manifest.read_text().splitlines():
        name = line.split()[1]
        shutil.copyfile(ROOT / name, tmp_path / name)
    return tmp_path


def test_runner_refuses_frozen_drift_before_any_build_or_gate(tmp_path, monkeypatch):
    directory = frozen_copy(tmp_path)
    (directory / "protocol.md").write_text("changed frozen protocol")
    monkeypatch.setattr(run_experiment, "HERE", directory)
    monkeypatch.setattr(sys, "argv", ["run_experiment.py"])
    monkeypatch.setenv("CONFIRM_RUN", "1")

    def forbidden(*args, **kwargs):
        raise AssertionError("A drifted study must stop before build, gates or reviewer setup")

    monkeypatch.setattr(run_experiment.build_payloads, "materialize_cases", forbidden)
    monkeypatch.setattr(run_experiment, "run_gate", forbidden)
    monkeypatch.setattr(run_experiment, "ReviewerClient", forbidden)
    with pytest.raises(SystemExit, match="frozen"):
        run_experiment.main()


def test_frozen_verification_matches_manifest_and_changes_nothing(tmp_path):
    from study_integrity import verify_frozen_files

    directory = frozen_copy(tmp_path)
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    assert len(verify_frozen_files(directory)) == 6
    assert {p.name: p.read_bytes() for p in directory.iterdir()} == before


@pytest.mark.parametrize("fault", ["missing", "duplicate", "omitted", "path", "symlink", "digest"])
def test_invalid_frozen_evidence_is_refused_without_repairs(tmp_path, fault):
    from study_integrity import verify_frozen_files

    directory = frozen_copy(tmp_path)
    manifest = directory / "DIGESTS.sha256"
    lines = manifest.read_text().splitlines()
    if fault == "missing":
        (directory / "protocol.md").unlink()
    elif fault == "duplicate":
        manifest.write_text("\n".join(lines + [lines[0]]) + "\n")
    elif fault == "omitted":
        manifest.write_text("\n".join(lines[1:]) + "\n")
    elif fault == "path":
        manifest.write_text(
            lines[0].replace("protocol.md", "../protocol.md") + "\n" + "\n".join(lines[1:]) + "\n"
        )
    elif fault == "symlink":
        target = directory / "protocol.md"
        original = directory / "other.md"
        target.rename(original)
        target.symlink_to(original)
    else:
        (directory / "protocol_k3.md").write_text("drift")
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    with pytest.raises(SystemExit, match="frozen"):
        verify_frozen_files(directory)
    assert {p.name: p.read_bytes() for p in directory.iterdir()} == before


def test_run_provenance_names_this_repository_commit():
    import subprocess

    expected = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert run_experiment.git_commit() == expected
