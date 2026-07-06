# SIMRS Khanza

Open-source Indonesian hospital management system (Sistem Informasi Manajemen Rumah Sakit).
Java Swing desktop app + PHP/JS web portals, backed by MariaDB/MySQL.

## Architecture
- `src/` — main desktop app (NetBeans/Ant). Entry point: `simrskhanza.SIMRSKhanza` (`main.class`).
  - `src/simrskhanza/` — main form + `Dlg*` workflow dialogs (registration, cashier, ranap, igd…)
  - `src/rekammedis/` — `RM*` medical-record / nursing-assessment forms
  - `src/fungsi/` — shared utils (`koneksiDB`, `akses`, `WarnaTable`, custom Swing widgets)
  - `src/bridging/`, `src/inventory/`, `src/laporan/` — integrations, pharmacy, reports
- `edokter/` `emcu/` `epasien/` `webapps/` — PHP + JS web portals (patient/doctor/MCU)
- `Khanza{Antrian*,HMS*}/` — 20+ standalone NetBeans sub-apps (queue kiosks, service bridges),
  each a self-contained Ant project with its own `build.xml` + `nbproject/`

## Build & Run (desktop app)
```bash
ant clean jar          # build → dist/SIMRSKhanza.jar  (or open in NetBeans)
ant run                # run via the NetBeans Ant target
```
Requires JDK + Apache Ant. Each `Khanza*` sub-app builds the same way from its own dir.

## Database
- MariaDB/MySQL. Schema/seed: `sik.sql` (+ `sik_bridging_lab.sql`, `sik_bridging_radiologi.sql`).
- Connection config lives in `setting/database.xml` and is **AES-encrypted**
  (`EnkripsiAES.decrypt`) — HOST/PORT/DATABASE are ciphertext, not plaintext. Do not hand-edit;
  generate values through the app's encryption path.

## Gotchas
- **Language:** all identifiers, UI, and DB columns are Bahasa Indonesia. Key terms:
  Ralan = rawat jalan (outpatient), Ranap = rawat inap (inpatient), IGD = emergency,
  RM = rekam medis (medical records), BPJS = national health insurance, resep = prescription.
- **God classes:** `frmUtama.java` is ~50k lines; `Dlg*` dialogs are 10k–21k lines each and mix
  UI + SQL + business logic. Use graphify to navigate before reading them whole.
- **Duplication:** infra classes (`koneksiDB`, `sekuel`, `WarnaTable`, widget wrappers) are
  copy-pasted into 10–18 sub-apps — no shared library. A fix must be applied in every copy.
  See the Appendix in `graphify-out/GRAPH_REPORT.md` for the full duplication + god-node map.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
