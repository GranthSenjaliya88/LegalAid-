from pathlib import Path

from corpus import loader


def test_official_snapshot_bundle_is_complete():
    files = sorted(loader.OFFICIAL_SNAPSHOTS_DIR.glob("*.official.json"))

    assert len(files) == 20
    assert sum(path.stat().st_size for path in files) > 10_000_000


def test_snapshot_loader_is_sorted_and_forces_updates(monkeypatch, tmp_path: Path):
    for filename in ("z.official.json", "a.official.json"):
        (tmp_path / filename).write_text("{}", encoding="utf-8")

    calls = []

    def fake_load_file(conn, path, force=False):
        calls.append((path.name, force))
        return loader.LoadResult(path.name, path.stem, 0, 0, 0, [])

    monkeypatch.setattr(loader, "load_file", fake_load_file)
    results = loader.load_official_snapshots(object(), snapshots_dir=tmp_path)

    assert [result.filename for result in results] == [
        "a.official.json",
        "z.official.json",
    ]
    assert calls == [
        ("a.official.json", True),
        ("z.official.json", True),
    ]
