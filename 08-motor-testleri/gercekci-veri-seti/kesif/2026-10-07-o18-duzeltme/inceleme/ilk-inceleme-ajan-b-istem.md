# Docs vs code consistency review

You are an independent reviewer of DOCUMENTATION against CODE. You have not seen how this change was made; that is the point. Be precise and skeptical: every number and every behavioural sentence in the documents must be checked against the code or flagged. Do not praise; report defects.

## Where things are
CODE (after the change, read-only):
  /tmp/claude-0/-home-claude/94f99f1c-acc5-50c9-9ce7-0966405f3d69/scratchpad/inceleme/yeni/09-motor/cozucu/coz.py
  .../inceleme/yeni/09-motor/cozucu/model.py
  .../inceleme/yeni/09-motor/testler/test_fazla_mesai_once_sifir.py
  .../inceleme/yeni/09-motor/testler/test_demir_secenekleri.py
  .../inceleme/yeni/09-motor/mutasyon_kostur.py
  .../inceleme/yeni/08-motor-testleri/gercekci-veri-seti/kalite-olc.py
  .../inceleme/yeni/08-motor-testleri/gercekci-veri-seti/testler/test_kalite_olc.py
DIFFS of the code and of two documents: .../inceleme/fark/*.diff
A runnable copy (Python + OR-Tools installed) if you want to check a claim empirically — you may only modify things under .../inceleme/calisir/ or create .../inceleme/ajan-b/ :
  `cd .../inceleme/calisir/09-motor && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest testler/test_fazla_mesai_once_sifir.py -q -p no:cacheprovider`   (26 tests, ~8 s)
  `python3 -m pytest testler/test_fazla_mesai_once_sifir.py --collect-only -q` to count tests. Note `import cozucu.coz` resolves to a function; use `importlib.import_module("cozucu.coz")` for the module.

DOCUMENTS to review (current versions; all in Turkish):
  /mnt/user-data/uploads/Tshift/02-spec/v1.4-master-spec.md
      - change-list row 60 (near line 117)
      - §6.7, the K-30 subsection and the NEW subsection "### Motor önce fazla mesaisiz plan arar" (near line 1454)
      - §11.3 rows `durma_sebebi`, `alt_sinir`, `fazla_mesaisiz_alt_sinir`, `fazla_mesai_once_sifir` (near lines 3620–3650)
      - §5.4 weight table (near line 854) for cross-checking numbers
  /mnt/user-data/uploads/Tshift/00-DEVIR/08-URUN-KARARLARI.md
      - the two NEW decision records at the very end: "## K-61" and "## K-62"; also the dated notes added under "## K-30" and "## K-50"
  /mnt/user-data/uploads/Tshift/00-DEVIR/06-ACIK-RISKLER.md
      - search for "bulgu 22" and read from "**6 Ekim 21:34–22:45" to the line starting "⚠ 0.1 ölçek sonuçları" (three dated blocks: 21:34–22:45, 23:02–23:15, 23:44–00:45), and the priority-table row that starts with "| **7** | **T-60"
  /mnt/user-data/uploads/Tshift/00-DEVIR/05-HATA-OTOPSILERI.md  — section "## O-17" and its row in the summary table
  /mnt/user-data/uploads/Tshift/00-DEVIR/00-BURADAN-BASLA.md — line 7 ("Son güncelleme") and the three paragraphs starting "**⚠ 6 Ekim 22:45", "**⚠ 6 Ekim 23:15", "**⚠ 7 Ekim 00:45"
  /mnt/user-data/uploads/Tshift/00-DEVIR/oturumlar/2026-10-06-uc-profil-ve-fazla-mesai-artigi.md — sections 12, 13, 14 and the table of contents at the top
  /mnt/user-data/uploads/Tshift/DEGISIM-GUNLUGU.md — the three newest entries at the top (2026-10-07 00:45, 2026-10-06 23:15, 2026-10-06 22:45)
  /mnt/user-data/uploads/Tshift/08-motor-testleri/gercekci-veri-seti/kesif/2026-10-06-veri-seti-merdiveni/OKU-BENI.md — an exploratory note the other documents cite

## Background you need
The engine's objective is a weighted sum of penalties. Product weights (per profile DENGELI / KAPSAMA / CALISAN): target shortfall HEDEF_KAPSAMA 9/20/5, HEDEF_ASIMI 3/1/4, MOLA_KAPSAMASI 7/9/6, ADALET_DENGESI 5/2/8, overtime FAZLA_MESAI 50 per MINUTE (so 3000 per hour). Decision K-61 (6 Oct 2026): the "overtime-free first" search (`fazla_mesai_once_sifir`) became the product default, with a guard: it is applied only when the per-minute overtime weight is >= the largest of the other penalty weights (function `_fazla_mesai_kisayolu_gecerli` in coz.py); otherwise it is skipped and the output says `{"uygulandi": False, "sebep": "agirlik", ...}`. The option only acts in the two-stage flow (`_ipucu_ver`, models with >= 50,000 variables). Decision K-62: a ladder of six 500-person data sets with known answers; staffing decisions (teams 285/145/70; dual-skilled people at all levels; night back-office minimum 2; "30 dual-skilled salespeople" is an ASSUMPTION the owner has not confirmed).
The owner (Mustafa) is a product manager, not a developer; documents must be understandable to both product and engineering readers, and every claim must be backed by code, a test, or a measurement. The project has a rule (called O-15) that the TOTAL count of killed mutations may only be claimed from a full run on the owner's machine; cloud "group runs" must be described as such.

## What to check
1. NUMBERS. Every number in the new/changed document passages that can be derived from code: weights (9/20/8 as "largest other weight" per profile — is 8 right for CALISAN? which term?), ratios (333 / 150 / 375), the example's scores (72, 9.000, 16.000, 180 minutes, 3 hours, 8 person-hours), test counts (26 in test_fazla_mesai_once_sifir.py with "10 new"; 18 in test_kalite_olc.py; verify by collecting), mutation counts (`fm_sifir` 44 with "15 new"; harness total 286 — count the tuples in mutasyon_kostur.py), "16 record configs pinned off" in kalite-olc.py, thresholds (50,000 variables; 120 s first-stage share; "en çok 120 sn"). Report each mismatch with both values and locations.
2. BEHAVIOUR SENTENCES. For each sentence describing what the engine does (when the note is emitted and its wording; what `null`/None means for `fazla_mesai_once_sifir`; what happens when the guard fails, including when the option is requested explicitly; whether small models are affected; what `uygulandi` means; `durma_sebebi` prefixes; which configs in kalite-olc inherit the default), find the code that implements it and flag any sentence the code contradicts or does not support.
3. INTERNAL CONSISTENCY between documents: do K-61, the spec §6.7 subsection, the §11.3 row, the ACIK-RISKLER block, BURADAN-BASLA paragraph, session log §14 and DEGISIM-GUNLUGU say the same thing (same condition, same numbers, same list of what is not measured, same next steps)? Do the three BURADAN-BASLA paragraphs / ACIK-RISKLER "Sıradaki adım" paragraphs leave an unambiguous CURRENT next step, or could a newcomer follow a superseded one? Is the staffing assumption "30" marked as unconfirmed everywhere it appears?
4. OVERSTATEMENT. Flag wording that claims more than what was shown: e.g. anything that reads as if the full mutation run or the 500-person verification already happened, as if the guard were a proof, as if the forced-overtime case were measured at full scale, as if small-scale exploratory numbers (49 and 151 people, single runs) were product measurements.
5. READABILITY for a product manager: sentences in the spec §6.7 subsection and in K-61/K-62 that use unexplained jargon or internal codes in a way that blocks understanding, or tables whose columns are ambiguous. Keep this part short (max 6 items) and only where it genuinely blocks understanding.
6. Markdown hygiene that would break tooling: a repo script flags any text of the form `N/N` or `N / N` where both numbers are equal 2–3 digit numbers >= 20 as a "test count claim", and flags back-ticked strings ending in a file extension (`.md`, `.py`, `.json`, ...) that do not exist in the repo (paths containing "/" must exist relative to the repo root, the document's folder, or `00-DEVIR/`). Search the new passages for such patterns (you cannot check existence of repo paths that are not under /mnt/user-data/uploads/Tshift, but list any back-ticked path with an extension that looks suspicious or abbreviated).

## Output format
A ranked list of findings, most severe first. Each: severity (WRONG / UNSUPPORTED / INCONSISTENT / OVERSTATED / UNCLEAR / NIT), document + line number (or a short quoted anchor), what it says, what the code or the other document says (with file + line), and a suggested corrected wording in Turkish when the fix is a wording change. Finish with a short "Checked and correct" list (one line each) so I know what you verified. Do not modify any document; do not write outside .../inceleme/ajan-b/ and .../inceleme/calisir/.