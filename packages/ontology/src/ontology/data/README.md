# Ontology data

Phong thủy knowledge as versioned YAML. Treat this like a database schema.

## Files

- `ngu_hanh.yaml` — Five elements with sinh (generates) and khắc (overcomes) relations.
- `huong.yaml` — Eight directions with degree ranges and seated trigrams.
- `cung_menh.yaml` — Eight personal trigrams (cung mệnh) with element, group, primary direction.
- `bat_trach.yaml` — 8×8 Bát Trạch table: relation type and score for every (cung, huong) pair.

## Conventions

- Keys are lowercase ASCII, Vietnamese-rooted (`tay_bac`, `cung_can`, `ngu_hanh_kim`).
- `cung_can` is Càn (Heaven, ☰). `cung_can_son` is Cấn (Mountain, ☶) — disambiguated because both are romanized "can" without diacritics.
- Each entity carries `label_vi` and `label_en` for UI.
- Scores in `bat_trach.yaml`: +4 best (sinh_khi), +1 neutral (phuc_vi), -4 worst (tuyet_menh).

## Validation status

⚠️ The current data is a **baseline** based on standard Bát Trạch references. **Before production use**, have an expert validate:

1. The 8×8 bát trạch table — schools may disagree on some pairs.
2. Direction degree ranges — some texts use slightly different boundaries.
3. The cung mệnh computation formula in `packages/ontology/src/ontology/query.py` is not implemented; the chosen school determines it.
