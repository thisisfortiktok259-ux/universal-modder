"""Offline contract tests for Codex image generation handoff."""

import hashlib
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from um import assets, publish


def png(path, *, transparent=True):
    color = (20, 40, 60, 0 if transparent else 255)
    Image.new("RGBA", (3, 2), color).save(path)
    return path


def brief(tmp_path, **kwargs):
    out = tmp_path / "generated"
    result = assets.request("a blue robot sprite", str(out), "robot", **kwargs)
    return Path(result["request"])


def fails_with(message, action, capsys):
    with pytest.raises(SystemExit) as exc:
        action()
    assert exc.value.code != 0
    assert message in capsys.readouterr().err


def test_request_writes_only_json_without_network_or_keys(tmp_path, monkeypatch):
    def deny_network(*_args, **_kwargs):
        raise AssertionError("network access attempted")

    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(socket.socket, "connect", deny_network)
    result = assets.request("a blue robot sprite", str(tmp_path / "generated"), "robot")
    request_path = Path(result["request"])
    assert sorted(p.name for p in request_path.parent.iterdir()) == ["robot.request.json"]
    data = json.loads(request_path.read_text(encoding="utf-8"))
    assert data["prompt"] == "a blue robot sprite"
    assert data["transparent_background"] is True
    assert result["status"] == "awaiting_image_generation"


def test_edit_request_records_relative_reference_and_hash(tmp_path):
    reference = png(tmp_path / "reference.png")
    request_path = brief(tmp_path, kind="edit", refs=[str(reference)])
    data = json.loads(request_path.read_text(encoding="utf-8"))
    assert data["references"] == [{
        "path": "../reference.png",
        "sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
    }]


def test_edit_request_requires_reference(tmp_path, capsys):
    fails_with("at least one --ref", lambda: brief(tmp_path, kind="edit"), capsys)
    assert not (tmp_path / "generated").exists()


@pytest.mark.parametrize("name", ["../outside", "bad/name", "CON", "lpt1", "a" * 65])
def test_request_rejects_unsafe_asset_name(tmp_path, capsys, name):
    fails_with("asset name", lambda: assets.request("robot", str(tmp_path / "generated"), name), capsys)
    assert not (tmp_path / "generated").exists()


def test_request_rejects_blank_prompt(tmp_path, capsys):
    fails_with("prompt cannot be empty", lambda: assets.request("  \t", str(tmp_path / "generated"), "robot"), capsys)
    assert not (tmp_path / "generated").exists()


def test_import_preserves_png_bytes_and_records_provenance(tmp_path):
    request_path = brief(tmp_path)
    source = png(tmp_path / "rendered.png")
    content = source.read_bytes()
    result = assets.import_image(str(source), str(request_path))
    target = request_path.parent / "robot.png"
    record = json.loads((request_path.parent / "assets_manifest.jsonl").read_text(encoding="utf-8"))
    assert target.read_bytes() == content
    assert result["sha256"] == record["sha256"] == hashlib.sha256(content).hexdigest()
    assert (record["provider"], record["model"], record["generation_verified"]) == (
        "codex-native-imagegen", "unspecified", False,
    )


def test_import_registers_png_already_saved_at_final_path(tmp_path):
    request_path = brief(tmp_path)
    target = png(request_path.parent / "robot.png")
    original = target.read_bytes()
    result = assets.import_image(str(target), str(request_path))
    records = (request_path.parent / "assets_manifest.jsonl").read_text(encoding="utf-8").splitlines()
    assert target.read_bytes() == original
    assert result["file"] == str(target)
    assert len(records) == 1
    assert json.loads(records[0])["sha256"] == hashlib.sha256(original).hexdigest()


def test_import_rejects_opaque_sprite(tmp_path, capsys):
    request_path = brief(tmp_path)
    source = png(tmp_path / "opaque.png", transparent=False)
    fails_with("real transparency", lambda: assets.import_image(str(source), str(request_path)), capsys)
    assert not (request_path.parent / "robot.png").exists()


def test_import_rejects_missing_request(tmp_path, capsys):
    source = png(tmp_path / "rendered.png")
    fails_with("cannot read request", lambda: assets.import_image(str(source), str(tmp_path / "missing.json")), capsys)


def test_import_rejects_malformed_request(tmp_path, capsys):
    request_path = tmp_path / "bad.json"
    request_path.write_text("{not json", encoding="utf-8")
    source = png(tmp_path / "rendered.png")
    fails_with("cannot read request", lambda: assets.import_image(str(source), str(request_path)), capsys)


def test_import_rejects_missing_png(tmp_path, capsys):
    request_path = brief(tmp_path)
    fails_with("cannot read PNG", lambda: assets.import_image(str(tmp_path / "missing.png"), str(request_path)), capsys)


def test_import_rejects_malformed_png(tmp_path, capsys):
    request_path = brief(tmp_path)
    source = tmp_path / "broken.png"
    source.write_bytes(b"not an image")
    fails_with("cannot read PNG", lambda: assets.import_image(str(source), str(request_path)), capsys)


def test_request_does_not_overwrite_existing_brief(tmp_path, capsys):
    request_path = brief(tmp_path)
    original = request_path.read_bytes()
    fails_with("request already exists", lambda: brief(tmp_path), capsys)
    assert request_path.read_bytes() == original


def test_import_does_not_overwrite_existing_png(tmp_path, capsys):
    request_path = brief(tmp_path)
    source = png(tmp_path / "rendered.png")
    target = request_path.parent / "robot.png"
    target.write_bytes(b"original")
    fails_with("asset already exists", lambda: assets.import_image(str(source), str(request_path)), capsys)
    assert target.read_bytes() == b"original"
    assert not (request_path.parent / "assets_manifest.jsonl").exists()


@pytest.mark.parametrize("change", ["edit", "delete"])
def test_import_rejects_changed_or_missing_reference_without_output(tmp_path, capsys, change):
    reference = png(tmp_path / "reference.png")
    request_path = brief(tmp_path, kind="edit", refs=[str(reference)])
    source = png(tmp_path / "rendered.png")
    if change == "edit":
        png(reference, transparent=False)
    else:
        reference.unlink()
    fails_with("reference changed or is missing", lambda: assets.import_image(str(source), str(request_path)), capsys)
    assert not (request_path.parent / "robot.png").exists()
    assert not (request_path.parent / "assets_manifest.jsonl").exists()


def test_cli_exposes_assets_group_and_removes_fal_group():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-m", "um", "--help"], cwd=root, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "assets" in result.stdout
    assert "fal" not in result.stdout


def test_cli_assets_help_explains_local_handoff():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-m", "um", "assets", "--help"], cwd=root, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "request" in result.stdout and "import" in result.stdout
    assert "No API key or network calls" in result.stdout


def test_publish_warns_when_generated_assets_lack_codex_credit(tmp_path, capsys):
    mod = tmp_path / "mod"
    mod.mkdir()
    (mod / "README.md").write_text("An example mod.\n", encoding="utf-8")
    (mod / "assets_manifest.jsonl").write_text("{}\n", encoding="utf-8")
    assert publish.check(str(mod)) == 0
    assert "no source credit line" in capsys.readouterr().out


def test_publish_accepts_codex_credit_for_generated_assets(tmp_path, capsys):
    mod = tmp_path / "mod"
    mod.mkdir()
    (mod / "README.md").write_text("Art generated with Codex.\n", encoding="utf-8")
    (mod / "assets_manifest.jsonl").write_text("{}\n", encoding="utf-8")
    assert publish.check(str(mod)) == 0
    out = capsys.readouterr().out
    assert "no source credit line" not in out
    assert "PASS:" in out


def test_publish_accepts_actual_local_art_credit(tmp_path, capsys):
    (tmp_path / "README.md").write_text("Art credits: hand drawn by the mod author.\n", encoding="utf-8")
    (tmp_path / "assets_manifest.jsonl").write_text("{}\n", encoding="utf-8")
    assert publish.check(str(tmp_path)) == 0
    assert "PASS:" in capsys.readouterr().out
