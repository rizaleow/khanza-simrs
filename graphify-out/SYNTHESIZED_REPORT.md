# Synthesized Bridge Report

**Input:** `graphify-out/graph.json` (349,812 edges)
**Output:** `graphify-out/graph_synthesized.json` (352,645 edges = 349,812 original + 2,833 synthesized)
**Time:** 2.6s

## What this script does

The graphify import resolver mis-routes or drops imports for `fungsi.*` shared
infra classes (WarnaTable, akses, koneksiDB, sekuel, validasi, batasInput,
closingkasir). The graph *does* capture these classes being used as field
types via `references field` edges to `<file>_java_<fieldname>` field-ref
nodes. This script synthesizes `imports` edges from each dialog class to
the matching canonical `src/fungsi/*` class based on the field type.

Synthesized edges are marked:
- `relation`: `imports`
- `confidence`: `INFERRED`
- `confidence_score`: 0.65 (weak inference, no shape evidence — only field-type match)
- `context`: `synthesized_from_field_type`
- `weight`: 0.5 (treat as soft signal, half of EXTRACTED)

## Per-target synthesis counts

| Target | Existing imports | + Synthesized | Total after |
|---|---:|---:|---:|
| `validasi` (src_fungsi_validasi_validasi) | 0 | +1514 | **1514** |
| `sekuel` (src_fungsi_sekuel_sekuel) | 0 | +1319 | **1319** |
| `WarnaTable` (src_fungsi_warnatable_warnatable) | 0 | +0 | **0** |
| `akses` (src_fungsi_akses_akses) | 0 | +0 | **0** |
| `koneksiDB` (src_fungsi_koneksidb_koneksidb) | 0 | +0 | **0** |
| `batasInput` (src_fungsi_batasinput_batasinput) | 0 | +0 | **0** |
| `WarnaTable2` (src_fungsi_warnatable2_warnatable2) | 66 | +0 | **66** |
| `WarnaTable3` (src_fungsi_warnatable3_warnatable3) | 9 | +0 | **9** |
| `WarnaTable4` (src_fungsi_warnatable4_warnatable4) | 0 | +0 | **0** |
| `WarnaTable5` (src_fungsi_warnatable5_warnatable5) | 0 | +0 | **0** |
| `cacheregistrasi` (src_fungsi_cacheregistrasi) | 2 | +0 | **2** |
| `catatanpasien` (src_fungsi_catatanpasien) | 4 | +0 | **4** |
| `closingkasir` (src_fungsi_closingkasir) | 3 | +0 | **3** |

## Top 25 bridges by incoming imports (after synthesis)

| # | Total | Real | Synth | Class | Source file |
|---|---:|---:|---:|---|---|
| 1 | 1514 | 0 | +1514 | `validasi` ⭐ | `src/fungsi/validasi.java` |
| 2 | 1319 | 0 | +1319 | `sekuel` ⭐ | `src/fungsi/sekuel.java` |
| 3 | 1259 | 1259 | +0 | `WarnaTable` | `KhanzaAntrianPoli/src/fungsi/WarnaTable.java` |
| 4 | 934 | 934 | +0 | `JTable` | `` |
| 5 | 440 | 440 | +0 | `RS SIMRS KHANZA branding (Guwosari, Pajangan, Bantul)` | `esign/file.pdf` |
| 6 | 205 | 205 | +0 | `DlgCariPetugas` | `src/kepegawaian/DlgCariPetugas.java` |
| 7 | 176 | 176 | +0 | `ActionListener` | `` |
| 8 | 102 | 102 | +0 | `JPanel` | `` |
| 9 | 100 | 100 | +0 | `DlgCariDokter` | `src/kepegawaian/DlgCariDokter.java` |
| 10 | 97 | 97 | +0 | `DlgCariPetugas.java` | `src/kepegawaian/DlgCariPetugas.java` |
| 11 | 94 | 94 | +0 | `Jurnal` | `src/keuangan/Jurnal.java` |
| 12 | 73 | 73 | +0 | `DlgCariCaraBayar.java` | `src/simrskhanza/DlgCariCaraBayar.java` |
| 13 | 66 | 66 | +0 | `WarnaTable2` ⭐ | `src/fungsi/WarnaTable2.java` |
| 14 | 63 | 63 | +0 | `DlgCariBangsal.java` | `src/simrskhanza/DlgCariBangsal.java` |
| 15 | 54 | 54 | +0 | `DlgCariPegawai.java` | `src/kepegawaian/DlgCariPegawai.java` |
| 16 | 50 | 50 | +0 | `ComponentListener` | `` |
| 17 | 41 | 41 | +0 | `JDialog` | `` |
| 18 | 36 | 36 | +0 | `DlgCariCaraBayar` | `src/simrskhanza/DlgCariCaraBayar.java` |
| 19 | 32 | 32 | +0 | `EnkripsiAES.java` | `KhanzaSecurity16bit/src/AESsecurity/EnkripsiAES.java` |
| 20 | 22 | 22 | +0 | `RMRiwayatPerawatan.java` | `src/rekammedis/RMRiwayatPerawatan.java` |
| 21 | 19 | 19 | +0 | `DlgKabupaten.java` | `src/simrskhanza/DlgKabupaten.java` |
| 22 | 18 | 18 | +0 | `DefaultTableCellRenderer` | `` |
| 23 | 18 | 18 | +0 | `lokasidepoutama.java` | `src/fungsi/lokasidepoutama.java` |
| 24 | 18 | 18 | +0 | `DlgKecamatan.java` | `src/simrskhanza/DlgKecamatan.java` |
| 25 | 18 | 18 | +0 | `DlgKelurahan.java` | `src/simrskhanza/DlgKelurahan.java` |

## Bridge score: synthesized vs original god-nodes

The original `GRAPH_REPORT.md` god-nodes list ranked these 10 nodes
by *total* degree (mostly `method` self-declarations):

| Original rank | Node | Old degree | Old in-degree (real) | New in-degree (after synthesis) |
|---:|---|---:|---:|---:|
| 1 | `khanzaantrianpoli_src_fungsi_warnatable_warnatable` | 2526 | 3782 | **2523** |
| 2 | `src_simrskhanza_frmutama_frmutama` | 1310 | 1 | **1** |
| 3 | `src_fungsi_akses_akses` | 1254 | 0 | **0** |
| 4 | `khanzacetakantrianloket_src_fungsi_akses_akses` | 883 | 0 | **0** |
| 5 | `src_kepegawaian_dlgcaripetugas_dlgcaripetugas` | 697 | 863 | **658** |
| 6 | `src_simrskhanza_dlgreg_dlgreg` | 491 | 0 | **0** |
| 7 | `src_simrskhanza_dlgkasirralan_dlgkasirralan` | 460 | 0 | **0** |
| 8 | `concept_rs_simrs_khanza_branding` | 442 | 882 | **442** |
| 9 | `src_simrskhanza_dlgrawatjalan_dlgrawatjalan` | 381 | 8 | **8** |
| 10 | `src_simrskhanza_dlgkamarinap_dlgkamarinap` | 378 | 0 | **0** |

## How to use the synthesized graph

The synthesized edges are flagged with `context: synthesized_from_field_type`
and `confidence_score: 0.65`. To use them in analysis:

- **For 'which dialogs depend on X' queries:** include synthesized edges
  (`confidence_score >= 0.6` filters EXTRACTED + synthesized INFERRED)
- **For 'is this a true god node' questions:** require `confidence_score = 1.0`
  (only EXTRACTED)
- **For 'which dialogs definitely use X' audit:** require EXTRACTED only
  and accept that the true count is higher (synthesized is the floor estimate)

## Caveats

1. The synthesis is based on field-type matches. If a dialog uses a
   `fungsi.X` class WITHOUT declaring it as a field (e.g., as a static
   singleton like `akses.getform()`), the import won't be synthesized
   because there's no field reference. This is the *most-called* case
   for `akses` (602 call sites in DlgReg.java alone) — those still won't
   show up unless you run the graphify resolver fix.
2. The synthesis picks the *first* canonical class with a matching label.
   For `WarnaTable` (5 variants) this picks the canonical `WarnaTable`,
   not the 2/3/4/5 variants. That's a deliberate choice — the canonical
   is the workhorse per the project CLAUDE.md.
3. The graph is not re-clustered. Communities are unchanged from the
   original. To recompute communities after synthesis, re-run
   `graphify cluster-only .` on the synthesized graph.
