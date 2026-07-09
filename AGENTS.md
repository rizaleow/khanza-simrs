# SIMRS Khanza

Open-source Indonesian hospital management system (Sistem Informasi Manajemen Rumah Sakit).
Java Swing desktop app + PHP/JS web portals, MariaDB/MySQL backend.

## Build & run (desktop app)

Ant-based, standard NetBeans project layout. Run from repo root.

```bash
ant clean jar          # → dist/SIMRSKhanza.jar
ant run                # runs main.class = simrskhanza.SIMRSKhanza
```

Each `Khanza*` sub-app builds the same way from its own dir (self-contained `build.xml` + `nbproject/`).
No automated test suite (`no src/test/`); `build-impl.xml` supports `test` target but nothing to run.

## Architecture

- `src/simrskhanza/` — `Dlg*` workflow dialogs (registration, cashier, ranap, igd…), main form `frmUtama.java`
- `src/rekammedis/` — `RM*` medical-record / nursing-assessment forms
- `src/fungsi/` — shared utils: `koneksiDB` (DB connection), `akses` (auth), `WarnaTable` (table renderer), custom Swing widget wrappers
- `src/bridging/`, `src/inventory/`, `src/laporan/` — BPJS/INACBG/Satu Sehat integrations, pharmacy, reports
- `edokter/` `emcu/` `epasien/` `webapps/` — PHP + JS web portals (patient/doctor/MCU)
- `Khanza{Antrian*,HMS*}/` — 20+ standalone sub-apps (queue kiosks, service bridges), each a copy-paste variant of the main app

## Database

MariaDB/MySQL. Schema: `sik.sql` (+ `sik_bridging_lab.sql`, `sik_bridging_radiologi.sql`).
Connection config in `setting/database.xml` is **AES-encrypted** — HOST/PORT/DATABASE are ciphertext.
Generate new values through the app's encryption path (`EnkripsiAES`), not by hand-editing XML.

## Critical gotchas

- **Bahasa Indonesia everywhere**: all identifiers, UI strings, DB columns. Ralan = rawat jalan (outpatient), Ranap = rawat inap (inpatient), IGD = emergency, RM = rekam medis, BPJS = national health insurance, resep = prescription.
- **God classes**: `frmUtama.java` is ~50k lines; `Dlg*` dialogs are 10k–21k lines each, mixing UI + SQL + business logic. Use the knowledge graph (below) to navigate before reading them whole.
- **Copy-paste duplication**: infra classes (`koneksiDB`, `sekuel`, `WarnaTable`, widget wrappers, `frmUtama` itself) exist in 10–18 sub-app directories as near-identical copies. **No shared library.** A fix must be applied in every copy. `graphify explain "<class>"` returns every copy location.
- **No package manager / lockfile** — deps are not declared anywhere. `lib/` is empty. The project assumes a classpath of JDK + JDBC drivers + SwingLayout jars + a few libs (`EnkripsiAES` depends on Bouncy Castle). See `nbproject/project.properties` for the resolved classpath.

## Knowledge graph (graphify)

A persistent knowledge graph lives at `graphify-out/`. Use it instead of grepping raw files for codebase questions.

Commands (run from repo root):
```bash
graphify query "<question>"          # BFS, scoped subgraph for a question
graphify query "<question>" --dfs    # trace a specific path
graphify path "<A>" "<B>"            # shortest path between two concepts
graphify explain "<concept>"         # plain-language summary of a node
graphify update .                    # incremental rebuild after edits (AST only, free)
```

Artifacts:
- `graphify-out/graph.json` — full graph (188MB). Loaded by `graphify query`.
- `graphify-out/GRAPH_REPORT.md` — audit report. Read for broad architecture review, NOT for narrow questions.
- `graphify-out/graph.html` — interactive community-aggregated view. Open in browser.
- `graphify-out/cache/` — AST + semantic extraction cache. Don't delete unless force-rebuilding.
- `graphify-out/graph_synthesized_v2.json` (154MB) — synthesized import edges working around an AST resolver bug; see below.

Rules:
- For codebase questions, **run `graphify query` first**. Don't grep the source tree before querying.
- The graph is persisted; `graphify update .` after edits keeps it current (no LLM cost — AST only).
- `GRAPH_REPORT.md` is a starting point for broad review, not for answering specific questions.

## Known graph artifacts

The AST import resolver has a bug that mis-routes or drops imports for shared `fungsi.*` classes
(`WarnaTable`, `akses`, `koneksiDB`, `sekuel`, `validasi`, `batasInput`). In the raw `graph.json`:
- `WarnaTable` shows 1,259 imports — but they should land on `src/fungsi/WarnaTable.java`, not `KhanzaAntrianPoli/src/fungsi/WarnaTable.java`.
- `akses`, `koneksiDB`, `sekuel`, `validasi`, `batasInput` show **0 imports** despite being called thousands of times across the codebase.

The synthesized graph at `graphify-out/graph_synthesized_v2.json` repairs this via field-type
references and source-code grep. When answering questions about shared infra, query that file
(`graphify query --graph graph_synthesized_v2.json "<question>"` if supported, otherwise inspect
directly). See `graphify-out/SYNTHESIZED_REPORT_v2.md` for the full bridge ranking.

Don't file bugs about missing edges to `src/fungsi/{akses,koneksiDB,sekuel,validasi,batasInput}`
without first checking the synthesized graph.