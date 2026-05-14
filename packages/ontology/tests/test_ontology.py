"""Structural invariants for the ontology data.

These tests do not validate that the phong thủy semantics are *correct* — that
requires an expert. They verify that the data is internally consistent:
references resolve, counts match, every cell of the 8x8 table is present.
"""

import pytest
from ontology import Ontology, load_ontology
from ontology.query import bat_trach_for_cung, huong_for_cung


@pytest.fixture(scope="module")
def ontology() -> Ontology:
    return load_ontology()


def test_five_elements_present(ontology: Ontology) -> None:
    assert set(ontology.ngu_hanh) == {"kim", "moc", "thuy", "hoa", "tho"}


def test_sinh_cycle_closes(ontology: Ontology) -> None:
    """Kim → Thủy → Mộc → Hỏa → Thổ → Kim."""
    el = ontology.ngu_hanh
    chain = ["kim"]
    for _ in range(5):
        chain.append(el[chain[-1]].sinh)
    assert chain == ["kim", "thuy", "moc", "hoa", "tho", "kim"]


def test_khac_cycle_closes(ontology: Ontology) -> None:
    """Kim → Mộc → Thổ → Thủy → Hỏa → Kim."""
    el = ontology.ngu_hanh
    chain = ["kim"]
    for _ in range(5):
        chain.append(el[chain[-1]].khac)
    assert chain == ["kim", "moc", "tho", "thuy", "hoa", "kim"]


def test_eight_directions_present(ontology: Ontology) -> None:
    assert len(ontology.huong) == 8
    expected = {"bac", "dong_bac", "dong", "dong_nam", "nam", "tay_nam", "tay", "tay_bac"}
    assert set(ontology.huong) == expected


def test_each_direction_has_seated_trigram(ontology: Ontology) -> None:
    cung_keys = set(ontology.cung_menh)
    for h in ontology.huong.values():
        # Trigram in huong.yaml references cung_menh by its trigram short-key
        # (e.g. `kham`, not `cung_kham`). Check both forms.
        assert h.trigram in cung_keys or f"cung_{h.trigram}" in cung_keys, (
            f"huong {h.key} references unknown trigram {h.trigram}"
        )


def test_eight_cung_menh_present(ontology: Ontology) -> None:
    assert len(ontology.cung_menh) == 8


def test_cung_menh_groups_split_four_four(ontology: Ontology) -> None:
    dong = [c for c in ontology.cung_menh.values() if c.nhom == "dong_tu_menh"]
    tay = [c for c in ontology.cung_menh.values() if c.nhom == "tay_tu_menh"]
    assert len(dong) == 4
    assert len(tay) == 4


def test_bat_trach_has_64_entries(ontology: Ontology) -> None:
    assert len(ontology.bat_trach) == 64


def test_bat_trach_covers_every_pair(ontology: Ontology) -> None:
    pairs = {(r.cung, r.huong) for r in ontology.bat_trach}
    expected = {(c, h) for c in ontology.cung_menh for h in ontology.huong}
    missing = expected - pairs
    assert not missing, f"Missing bát trạch entries: {missing}"


def test_bat_trach_for_cung_returns_eight(ontology: Ontology) -> None:
    for cung_key in ontology.cung_menh:
        rels = bat_trach_for_cung(cung_key, ontology)
        assert len(rels) == 8


def test_each_cung_has_phuc_vi_at_its_home(ontology: Ontology) -> None:
    for cung in ontology.cung_menh.values():
        rel = huong_for_cung(cung.key, cung.huong_chinh, ontology)
        assert rel is not None
        assert rel.quan_he == "phuc_vi"


def test_each_cung_has_one_sinh_khi_one_tuyet_menh(ontology: Ontology) -> None:
    for cung_key in ontology.cung_menh:
        rels = bat_trach_for_cung(cung_key, ontology)
        sinh_khi = [r for r in rels if r.quan_he == "sinh_khi"]
        tuyet_menh = [r for r in rels if r.quan_he == "tuyet_menh"]
        assert len(sinh_khi) == 1, f"{cung_key} has {len(sinh_khi)} sinh_khi"
        assert len(tuyet_menh) == 1, f"{cung_key} has {len(tuyet_menh)} tuyet_menh"


def test_score_sum_is_zero_per_cung(ontology: Ontology) -> None:
    """+4+3+2+1-1-2-3-4 = 0 for each cung. A simple checksum on the table."""
    for cung_key in ontology.cung_menh:
        rels = bat_trach_for_cung(cung_key, ontology)
        assert sum(r.diem for r in rels) == 0
