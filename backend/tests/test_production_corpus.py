from pathlib import Path

from corpus import loader


def test_official_snapshot_bundle_is_complete():
    files = sorted(loader.OFFICIAL_SNAPSHOTS_DIR.glob("*.official.json"))

    assert len(files) >= 35
    assert sum(path.stat().st_size for path in files) > 13_000_000

    expanded_bundle = {
        "hindu_marriage_act_1955.official.json",
        "pocso_act_2012.official.json",
        "right_to_education_act_2009.official.json",
        "rera_act_2016.official.json",
        "maternity_benefit_act_1961.official.json",
        "code_of_civil_procedure_1908.official.json",
        "legal_services_authorities_act_1987.official.json",
    }
    assert expanded_bundle.issubset({path.name for path in files})


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
