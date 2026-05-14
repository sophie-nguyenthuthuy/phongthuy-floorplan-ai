# Phong thủy school decision

**Decision (v0.1):** Use the **traditional Bát Trạch Minh Cảnh** school (Bát Trạch Minh Cảnh / 八宅明鏡).

## Why not Lạc Việt

The Lạc Việt school (Nguyễn Vũ Tuấn Anh) is a Vietnamese revisionist school that swaps the trigrams **Khôn ↔ Cấn** in the bát trạch table relative to the traditional Chinese-derived system. It is a single-author school.

Arguments against using it as our default:

1. **Market reach.** The overwhelming majority of practicing VN phong thủy masters and published references use the traditional system. Aligning with traditional makes our results legible to practitioners and consistent with what users learned from family/elders.
2. **Internal consistency.** Lạc Việt only changes the bát trạch table; the rest of the system (cung mệnh formula, ngũ hành relations, hướng) is identical. Adopting just the swap creates internal tension with imported feng shui literature.
3. **Verifiability.** Traditional bát trạch has a thousand-year written record. Lạc Việt rests on a single author's interpretation of the I Ching.

## What this commits us to

The 8×8 bát trạch table in `packages/ontology/src/ontology/data/bat_trach.yaml` follows the traditional mapping. Specifically: **Khôn ↔ Tây Nam**, **Cấn ↔ Đông Bắc**, with sinh_khi/thien_y/dien_nien/phuc_vi distribution matching standard references.

The `cung_menh_from_birth` formula uses the standard digit-sum reduction with:

- Male: `cung = 10 - S`, with `5 → Khôn`
- Female: `cung = (S + 5) mod 9` (0 → 9), with `5 → Cấn`

where `S` is the digit sum of the **phong thủy year**, reduced to a single digit.

The phong thủy year is the solar year starting on **Lập Xuân (~Feb 4)**. Births on Jan 1 – Feb 3 inclusive are counted as the previous year. (Lập Xuân falls on Feb 3, 4, or 5 depending on the astronomical calendar — we use Feb 4 as a fixed cutoff for now; the residual error affects <1% of births and the convention is consistent with widely-used VN phong thủy software.)

## Future: making the school configurable

If we later want to support Lạc Việt as an opt-in mode, the cleanest path is:

1. A second YAML file `bat_trach_lac_viet.yaml` that overrides only the swapped entries.
2. A `school: "traditional" | "lac_viet"` parameter on `load_ontology()`.
3. Document the choice prominently in the UI so users know which interpretation they're seeing.

No code structure changes needed — the data is already swappable.

## References

- Bát Trạch Minh Cảnh (八宅明鏡), Triệu Cửu Phong, Qing dynasty.
- Kinh Dịch và cấu hình tiên thiên, traditional Hán-Việt commentaries.
- The 8×8 table our `bat_trach.yaml` encodes is the same one tabulated in standard references e.g. Stephen Skinner's *Feng Shui*, Eva Wong's *Feng-Shui*, and contemporary VN phong thủy texts (Tả Ao, Hoàng Xuân Lộc, etc.).

## Validation status

⚠️ **Before any commercial release**, the table and formula must be reviewed by a practicing VN phong thủy expert. The structural invariants in `test_ontology.py` and reference-value tests in `test_cung_menh_correctness.py` catch implementation bugs but not domain errors.
