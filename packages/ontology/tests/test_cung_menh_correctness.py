"""Reference-value tests for `cung_menh_from_birth`.

The table below is derived from the traditional Bát Trạch Minh Cảnh formula:

    S = digit sum of phong thủy year, reduced to 1..9
    Male:   idx = 10 - S       (5 → Khôn)
    Female: idx = (S + 5) red. (5 → Cấn)

Cross-check these values against any published VN phong thủy reference (e.g.
the cung-mệnh tables in Hoàng Xuân Lộc, *Phong Thủy Toàn Thư*, or any modern
VN phong thủy app). If a reference disagrees on a row, that row must be
audited before trusting the implementation in production.
"""

from datetime import date

import pytest
from ontology.query import _digit_sum_to_single, _phong_thuy_year, cung_menh_from_birth

# (year, male_cung, female_cung)
# Mid-year birth (June 15) so the Feb 4 cutoff doesn't affect the year.
REFERENCE_TABLE: list[tuple[int, str, str]] = [
    (1980, "cung_kham", "cung_can_son"),  # S=9
    (1981, "cung_ly", "cung_can"),  # S=1
    (1982, "cung_can_son", "cung_doai"),  # S=2
    (1983, "cung_doai", "cung_can_son"),  # S=3
    (1984, "cung_can", "cung_ly"),  # S=4
    (1985, "cung_khon", "cung_kham"),  # S=5  (male: 5-exception → Khôn)
    (1986, "cung_ton", "cung_khon"),  # S=6
    (1987, "cung_chan", "cung_chan"),  # S=7
    (1988, "cung_khon", "cung_ton"),  # S=8
    (1989, "cung_kham", "cung_can_son"),  # S=9
    (1990, "cung_ly", "cung_can"),  # S=1
    (1991, "cung_can_son", "cung_doai"),  # S=2
    (1992, "cung_doai", "cung_can_son"),  # S=3
    (1993, "cung_can", "cung_ly"),  # S=4
    (1994, "cung_khon", "cung_kham"),  # S=5
    (1995, "cung_ton", "cung_khon"),  # S=6
    (1996, "cung_chan", "cung_chan"),  # S=7
    (1997, "cung_khon", "cung_ton"),  # S=8
    (1998, "cung_kham", "cung_can_son"),  # S=9
    (1999, "cung_ly", "cung_can"),  # S=1
    (2000, "cung_can_son", "cung_doai"),  # S=2
    (2001, "cung_doai", "cung_can_son"),  # S=3
    (2002, "cung_can", "cung_ly"),  # S=4
    (2003, "cung_khon", "cung_kham"),  # S=5
    (2004, "cung_ton", "cung_khon"),  # S=6
    (2005, "cung_chan", "cung_chan"),  # S=7
    (1962, "cung_kham", "cung_can_son"),  # widely-cited reference: Nhâm Dần
    (1973, "cung_can_son", "cung_doai"),  # widely-cited reference: Quý Sửu
]


@pytest.mark.parametrize(("year", "male_cung", "female_cung"), REFERENCE_TABLE)
def test_cung_menh_matches_reference_male(year: int, male_cung: str, female_cung: str) -> None:
    assert cung_menh_from_birth(date(year, 6, 15), "nam") == male_cung


@pytest.mark.parametrize(("year", "male_cung", "female_cung"), REFERENCE_TABLE)
def test_cung_menh_matches_reference_female(year: int, male_cung: str, female_cung: str) -> None:
    assert cung_menh_from_birth(date(year, 6, 15), "nu") == female_cung


class TestLapXuanCutoff:
    def test_before_feb_4_uses_previous_year(self) -> None:
        # 1990 male → Ly; treated as 1989 → Khảm
        assert cung_menh_from_birth(date(1990, 1, 15), "nam") == "cung_kham"

    def test_feb_4_inclusive_uses_current_year(self) -> None:
        assert cung_menh_from_birth(date(1990, 2, 4), "nam") == "cung_ly"

    def test_feb_3_uses_previous_year(self) -> None:
        assert cung_menh_from_birth(date(1990, 2, 3), "nam") == "cung_kham"

    def test_dec_31_uses_current_year(self) -> None:
        assert cung_menh_from_birth(date(1990, 12, 31), "nam") == "cung_ly"

    def test_phong_thuy_year_helper(self) -> None:
        assert _phong_thuy_year(date(1990, 1, 15)) == 1989
        assert _phong_thuy_year(date(1990, 2, 4)) == 1990
        assert _phong_thuy_year(date(1990, 2, 3)) == 1989


class TestEdgeCases:
    def test_invalid_gender_raises(self) -> None:
        with pytest.raises(ValueError, match="gioi_tinh"):
            cung_menh_from_birth(date(1990, 6, 15), "other")  # type: ignore[arg-type]

    def test_digit_sum_reduction(self) -> None:
        assert _digit_sum_to_single(1990) == 1
        assert _digit_sum_to_single(9) == 9
        assert _digit_sum_to_single(18) == 9
        assert _digit_sum_to_single(28) == 1

    def test_all_eight_cung_reachable(self) -> None:
        """Across enough years × both genders, all 8 cung should appear."""
        from ontology.query import GioiTinh

        seen: set[str] = set()
        genders: tuple[GioiTinh, ...] = ("nam", "nu")
        for year in range(1950, 2030):
            for g in genders:
                seen.add(cung_menh_from_birth(date(year, 6, 15), g))
        assert len(seen) == 8
