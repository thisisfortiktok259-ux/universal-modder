"""Local handoff for assets generated with Codex's native image tool. No API key or network calls.

    um assets request "side-view robot sprite, facing left" --out assets/gen --name robot
    um assets request "same robot, walking" --kind edit --ref assets/gen/robot.png --name robot-walk
    um assets import generated.png --request assets/gen/robot.request.json

`request` writes a generation brief, not an image. The agent generates or edits the image in
the Codex chat, then `import` validates a local PNG and records its provenance. Standalone
Python cannot invoke the native chat tool. Audio, video and 3D generation are not provided.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from um.common import die, emit, to_posix

KINDS = ("sprite", "image", "texture", "edit")
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def _name(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) or value.upper() in RESERVED:
        die("asset name must be 1-64 letters/digits/hyphens/underscores, and not a reserved filename")
    return value


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _png(path: Path, transparent: bool = False) -> tuple[int, int]:
    try:
        with Image.open(path) as im:
            if im.format != "PNG":
                die(f"expected a PNG image: {path}")
            im.load()
            if transparent and im.convert("RGBA").getchannel("A").getextrema()[0] == 255:
                die("this request needs real transparency; generate transparent PNG or run `um sprite cutout` first")
            return im.size
    except (OSError, UnidentifiedImageError) as exc:
        die(f"cannot read PNG {path}: {exc}")


def request(prompt: str, out: str, name: str, kind: str = "sprite", refs=(), opaque: bool = False) -> dict:
    name = _name(name)
    if not prompt.strip():
        die("prompt cannot be empty")
    if kind not in KINDS:
        die(f"unsupported kind: {kind}")
    if kind == "edit" and not refs:
        die("editing needs at least one --ref PNG")
    folder = Path(to_posix(out)).resolve()
    references = []
    for ref in refs:
        path = Path(to_posix(ref)).resolve()
        _png(path)
        try:
            relative = os.path.relpath(path, folder)
        except ValueError:
            die("reference must be on the same drive as the output folder")
        references.append({"path": Path(relative).as_posix(), "sha256": _hash(path)})
    data = {
        "version": 1,
        "provider": "codex-native-imagegen",
        "kind": kind,
        "name": name,
        "prompt": prompt,
        "transparent_background": not opaque and kind in ("sprite", "edit"),
        "references": references,
    }
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{name}.request.json"
    try:
        with target.open("x", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    except FileExistsError:
        die(f"request already exists: {target}; use a new --name")
    tool_args = {"prompt": prompt, "transparent_background": data["transparent_background"]}
    if references:
        tool_args["referenced_image_paths"] = [str((folder / r["path"]).resolve()) for r in references]
    return {
        "status": "awaiting_image_generation",
        "request": str(target),
        "tool": "image_gen.imagegen",
        "tool_arguments": tool_args,
        "next": "Generate in the Codex chat, save the returned PNG, then run `um assets import <PNG> --request <request>`.",
    }


def import_image(source: str, request_path: str, model: str | None = None) -> dict:
    path = Path(to_posix(request_path)).resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        die(f"cannot read request: {exc}")
    if not isinstance(data, dict) or data.get("version") != 1 or data.get("provider") != "codex-native-imagegen":
        die("unsupported asset request")
    name = _name(data.get("name"))
    if data.get("kind") not in KINDS or not isinstance(data.get("prompt"), str) or not data["prompt"].strip():
        die("invalid asset request kind or prompt")
    if not isinstance(data.get("transparent_background"), bool) or not isinstance(data.get("references"), list):
        die("invalid asset request transparency or references")
    for ref in data["references"]:
        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str) or not isinstance(ref.get("sha256"), str):
            die("invalid reference in asset request")
        reference = (path.parent / ref["path"]).resolve()
        if not reference.is_file() or _hash(reference) != ref["sha256"]:
            die("reference changed or is missing; create a new request for the current image")
    src = Path(to_posix(source)).resolve()
    width, height = _png(src, transparent=data["transparent_background"])
    content = src.read_bytes()
    target = path.parent / f"{name}.png"
    if src != target.resolve():
        try:
            with target.open("xb") as f:
                f.write(content)
        except FileExistsError:
            die(f"asset already exists: {target}; use a new request name")
    record = {
        **data,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "file": target.name,
        "sha256": hashlib.sha256(content).hexdigest(),
        "width": width,
        "height": height,
        "model": model or "unspecified",
        "generation_verified": False,
    }
    # This verifies the imported file, not how the caller generated it.
    with (path.parent / "assets_manifest.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"status": "imported", "file": str(target), "sha256": record["sha256"], "width": width, "height": height}


def register(sub):
    p = sub.add_parser("assets", help="briefs and local PNG import for Codex image generation (no API key)",
                       description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cs = p.add_subparsers(dest="cmd", metavar="<cmd>")
    q = cs.add_parser("request", help="write a brief for the native chat image tool; does not generate an image")
    q.add_argument("prompt")
    q.add_argument("--out", default="assets/gen")
    q.add_argument("--name", required=True)
    q.add_argument("--kind", choices=KINDS, default="sprite")
    q.add_argument("--ref", action="append", default=[])
    q.add_argument("--opaque", action="store_true", help="allow an opaque background")
    q.set_defaults(func=lambda a: emit(request(a.prompt, a.out, a.name, a.kind, a.ref, a.opaque)))
    q = cs.add_parser("import", help="validate a generated local PNG, preserve its bytes, and append provenance")
    q.add_argument("source")
    q.add_argument("--request", required=True)
    q.add_argument("--model", help="actual model name only when known; otherwise recorded as unspecified")
    q.set_defaults(func=lambda a: emit(import_image(a.source, a.request, a.model)))
