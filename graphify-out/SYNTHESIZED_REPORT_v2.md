# Synthesized Bridge Report v2

**Input:** `graphify-out/graph.json` (349,719 edges)
**Output:** `graphify-out/graph_synthesized_v2.json` (357,816 edges)
**Time:** 39.1s

**Phase 1 (field-type):** 2,833 edges
**Phase 2 (source-code usage):** 5,264 edges
**Total synthesized:** 8,097

## The bug this works around

graphify's import resolver fails 4 ways for `fungsi.*` shared infra
classes (WarnaTable, akses, koneksiDB, sekuel, validasi, batasInput,
closingkasir). The graph captures the usages indirectly via field-type
references and source-code patterns, so we can recover the import edges
in two passes.

## Per-target synthesis counts

| Target | Real (original) | + Phase 1 (field) | + Phase 2 (source) | Total after |
|---|---:|---:|---:|---:|
| `validasi` | 0 | +1514 | +0 | **1514** |
| `koneksiDB` | 0 | +0 | +1405 | **1405** |
| `sekuel` | 0 | +1319 | +0 | **1319** |
| `WarnaTable` | 0 | +0 | +1272 | **1272** |
| `batasInput` | 0 | +0 | +1250 | **1250** |
| `akses` | 0 | +0 | +1245 | **1245** |
| `WarnaTable2` | 66 | +0 | +66 | **132** |
| `WarnaTable3` | 9 | +0 | +9 | **18** |
| `catatanpasien` | 4 | +0 | +4 | **8** |
| `closingkasir` | 3 | +0 | +3 | **6** |
| `WarnaTable4` | 0 | +0 | +5 | **5** |
| `cacheregistrasi` | 2 | +0 | +2 | **4** |
| `WarnaTable5` | 0 | +0 | +3 | **3** |

## Top 25 bridges by incoming imports (after v2 synthesis)

| # | Total | Real | Synth | Class | Source file |
|---|---:|---:|---:|---|---|
| 1 | 1514 | 0 | +1514 | `validasi` ⭐ | `src/fungsi/validasi.java` |
| 2 | 1405 | 0 | +1405 | `koneksiDB` ⭐ | `src/fungsi/koneksiDB.java` |
| 3 | 1319 | 0 | +1319 | `sekuel` ⭐ | `src/fungsi/sekuel.java` |
| 4 | 1272 | 0 | +1272 | `WarnaTable` ⭐ | `src/fungsi/WarnaTable.java` |
| 5 | 1259 | 1259 | +0 | `WarnaTable` | `KhanzaAntrianPoli/src/fungsi/WarnaTable.java` |
| 6 | 1250 | 0 | +1250 | `batasInput` ⭐ | `src/fungsi/batasInput.java` |
| 7 | 1245 | 0 | +1245 | `akses` ⭐ | `src/fungsi/akses.java` |
| 8 | 934 | 934 | +0 | `JTable` | `` |
| 9 | 440 | 440 | +0 | `RS SIMRS KHANZA branding (Guwosari, Pajangan, Bantul)` | `esign/file.pdf` |
| 10 | 205 | 205 | +0 | `DlgCariPetugas` | `src/kepegawaian/DlgCariPetugas.java` |
| 11 | 176 | 176 | +0 | `ActionListener` | `` |
| 12 | 132 | 66 | +66 | `WarnaTable2` ⭐ | `src/fungsi/WarnaTable2.java` |
| 13 | 102 | 102 | +0 | `JPanel` | `` |
| 14 | 100 | 100 | +0 | `DlgCariDokter` | `src/kepegawaian/DlgCariDokter.java` |
| 15 | 97 | 97 | +0 | `DlgCariPetugas.java` | `src/kepegawaian/DlgCariPetugas.java` |
| 16 | 94 | 94 | +0 | `Jurnal` | `src/keuangan/Jurnal.java` |
| 17 | 73 | 73 | +0 | `DlgCariCaraBayar.java` | `src/simrskhanza/DlgCariCaraBayar.java` |
| 18 | 63 | 63 | +0 | `DlgCariBangsal.java` | `src/simrskhanza/DlgCariBangsal.java` |
| 19 | 54 | 54 | +0 | `DlgCariPegawai.java` | `src/kepegawaian/DlgCariPegawai.java` |
| 20 | 50 | 50 | +0 | `ComponentListener` | `` |
| 21 | 41 | 41 | +0 | `JDialog` | `` |
| 22 | 36 | 36 | +0 | `DlgCariCaraBayar` | `src/simrskhanza/DlgCariCaraBayar.java` |
| 23 | 32 | 32 | +0 | `EnkripsiAES.java` | `KhanzaSecurity16bit/src/AESsecurity/EnkripsiAES.java` |
| 24 | 22 | 22 | +0 | `RMRiwayatPerawatan.java` | `src/rekammedis/RMRiwayatPerawatan.java` |
| 25 | 19 | 19 | +0 | `DlgKabupaten.java` | `src/simrskhanza/DlgKabupaten.java` |

## How the original god-nodes list compares

**Before** (from `GRAPH_REPORT.md`, ranked by total degree):

| Rank | Node | Old total degree | Was it a real bridge? |
|---:|---|---:|---|
| 1 | `WarnaTable` | 2526 | real_imports=1259 → 1259 after synthesis |
| 2 | `frmUtama` | 1310 | real_imports=0 → 0 after synthesis |
| 3 | `akses` | 1254 | real_imports=0 → 1245 after synthesis |
| 4 | `akses` | 883 | real_imports=0 → 0 after synthesis |
| 5 | `DlgCariPetugas` | 697 | real_imports=205 → 205 after synthesis |
| 6 | `DlgReg` | 491 | real_imports=0 → 0 after synthesis |
| 7 | `DlgKasirRalan` | 460 | real_imports=0 → 0 after synthesis |
| 8 | `RS SIMRS KHANZA branding (Guwosari, Pajangan, Bantul)` | 442 | real_imports=440 → 440 after synthesis |
| 9 | `DlgRawatJalan` | 381 | real_imports=0 → 0 after synthesis |
| 10 | `DlgKamarInap` | 378 | real_imports=0 → 0 after synthesis |

## Caveats

1. **Phase 1 (field-type)** synthesizes from real graph edges — high
   confidence (INFERRED 0.65).
2. **Phase 2 (source-code grep)** is a coarse signal: we don't check
   that the `new X(` or `X.method(` is in a *method body* of the
   class node (we just know the file uses the class). The confidence
   is lower (INFERRED 0.55).
3. We may also count the target's *own* .java file (e.g.,
   `src/fungsi/WarnaTable.java` uses `JTable` internally). We filter
   the target's own file out of the source-file list.
4. The graph is not re-clustered. To re-cluster with synthesized
   edges, run `graphify cluster-only .` on `graph_synthesized_v2.json`.
5. The synthesized graph has 2x the edges of the field-only
   synthesis. It is the most useful artifact for analysis even though
   it is noisier.
