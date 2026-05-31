from __future__ import annotations

from pathlib import Path


def test_frontend_runtime_does_not_import_static_mock_json():
    frontend_src = Path("frontend/src")
    runtime_files = [
        *frontend_src.rglob("*.ts"),
        *frontend_src.rglob("*.tsx"),
    ]

    offenders = []
    for path in runtime_files:
        text = path.read_text(encoding="utf-8")
        if "@/data/" in text or "src/data/" in text or "../data/" in text:
            offenders.append(str(path))

    assert offenders == []
    assert not (frontend_src / "data").exists()
