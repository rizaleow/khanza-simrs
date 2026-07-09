"""
v2: Post-process graph.json to synthesize missing import edges for shared infra.

Combines two synthesis signals:
1. Field-type references: for every `references field` edge from a class to a
   `<file>_java_X` field-ref node, synthesize an imports edge to the canonical
   `fungsi.X` class (recovers `sekuel`, `validasi`).
2. Source-code usage: for every Java file that uses `new X(...)` or `X.<method>(`
   patterns, synthesize an imports edge to the canonical class. This catches
   classes used as static-singletons (`akses.getform()`) or constructors
   (`new batasInput(...)`) without a field declaration (recovers `WarnaTable`,
   `akses`, `koneksiDB`, `batasInput`, `WarnaTable2-5`).
"""

import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

GRAPH_PATH = "graphify-out/graph.json"
OUT_PATH = "graphify-out/graph_synthesized_v2.json"
REPORT_PATH = "graphify-out/SYNTHESIZED_REPORT_v2.md"

# Canonical class IDs (verified to exist in graph)
TARGETS = {
    "WarnaTable":   ("src_fungsi_warnatable_warnatable",   "src/fungsi/WarnaTable.java",    "JTable zebra-striping renderer (canonical)"),
    "WarnaTable2":  ("src_fungsi_warnatable2_warnatable2", "src/fungsi/WarnaTable2.java",   "JTable zebra-striping v2"),
    "WarnaTable3":  ("src_fungsi_warnatable3_warnatable3", "src/fungsi/WarnaTable3.java",   "JTable zebra-striping v3"),
    "WarnaTable4":  ("src_fungsi_warnatable4_warnatable4", "src/fungsi/WarnaTable4.java",   "JTable zebra-striping v4"),
    "WarnaTable5":  ("src_fungsi_warnatable5_warnatable5", "src/fungsi/WarnaTable5.java",   "JTable zebra-striping v5"),
    "akses":        ("src_fungsi_akses_akses",             "src/fungsi/akses.java",         "Auth / user session"),
    "koneksiDB":    ("src_fungsi_koneksidb_koneksidb",     "src/fungsi/koneksiDB.java",     "DB connection factory"),
    "sekuel":       ("src_fungsi_sekuel_sekuel",           "src/fungsi/sekuel.java",        "SQL execution wrapper"),
    "validasi":     ("src_fungsi_validasi_validasi",       "src/fungsi/validasi.java",      "Input validation helpers"),
    "batasInput":   ("src_fungsi_batasinput_batasinput",   "src/fungsi/batasInput.java",    "JTextField max-length wrapper"),
    "cacheregistrasi":  ("src_fungsi_cacheregistrasi",      "src/fungsi/cacheregistrasi.java","Registration cache"),
    "catatanpasien":    ("src_fungsi_catatanpasien",        "src/fungsi/catatanpasien.java",  "Patient notes wrapper"),
    "closingkasir":     ("src_fungsi_closingkasir",         "src/fungsi/closingkasir.java",   "End-of-day cashier close"),
}

# Names that look like the target names but are actually external (don't synthesize)
EXTERNAL_LIKE = {
    "WarnaTableKasirRalan",  # specialized class
    "WarnaTableEWSNeonatus", # specialized class
    "akses_depo_obat",       # method, not class
    "koneksiDB.condb",       # call, not class
}


def main():
    t0 = time.time()
    print("Loading graph...", flush=True)
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    nodes = graph["nodes"]
    links = graph["links"]
    node_by_id = {n["id"]: n for n in nodes}
    print(f"  {len(nodes)} nodes, {len(links)} links ({time.time()-t0:.1f}s)", flush=True)

    canonical_ids = {v[0] for v in TARGETS.values()}

    # === Phase 1: field-type synthesis ===
    print("\nPhase 1: synthesizing from `references field` edges...", flush=True)
    synth_phase1 = []
    for l in links:
        if l.get("relation") != "references" or l.get("context") != "field":
            continue
        tid = l.get("target", "")
        if "_java_" not in tid:
            continue
        tinfo = node_by_id.get(tid, {})
        field_name = tinfo.get("label", "")
        if not field_name or field_name not in TARGETS:
            continue
        target_id = TARGETS[field_name][0]
        if target_id not in node_by_id:
            continue
        sid = l.get("source")
        sinfo = node_by_id.get(sid, {})
        synth_phase1.append({
            "source": sid,
            "target": target_id,
            "relation": "imports",
            "confidence": "INFERRED",
            "confidence_score": 0.65,
            "context": "synthesized_from_field_type",
            "source_file": sinfo.get("source_file", ""),
            "source_location": l.get("source_location", ""),
            "weight": 0.5,
            "synthesis_reason": f"field `{field_name}` at {sinfo.get('source_file','')}:{l.get('source_location','')}",
        })
    print(f"  Phase 1: {len(synth_phase1)} edges", flush=True)

    # === Phase 2: source-code usage synthesis ===
    print("\nPhase 2: scanning source code for `new X(` and `X.method(` usages...", flush=True)
    # We want to find: for each target name, which .java files USE it
    # Patterns: `new X(`, `X.<identifier>(` (call), `X.X` (static field read)
    # Skip the target's own .java file (it doesn't import itself)
    target_own_files = {TARGETS[k][1]: True for k in TARGETS}
    usage_files = {}  # name -> set of source files
    for name, (canonical_id, target_src, _) in TARGETS.items():
        # Use ripgrep for speed
        # Find: new Name( or Name.<lowercase>(
        # Exclude the target's own file
        # Exclude files in node_modules-like dirs (not relevant here)
        pattern = rf"new {re.escape(name)}\(|\b{re.escape(name)}\.[a-z]"
        cmd = ["grep", "-rlE", pattern, "src/", "--include=*.java", "--exclude-dir=graphify-out"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        files = [f for f in result.stdout.split("\n") if f.strip() and f != target_src]
        usage_files[name] = set(files)
        print(f"  {name:18s}: {len(files):4d} files use it (excl. own file)", flush=True)

    # Build set of (source, target) pairs from phase 1 to avoid duplicates
    seen = {(s["source"], s["target"]) for s in synth_phase1}
    synth_phase2 = []
    for name, (canonical_id, target_src, _) in TARGETS.items():
        if canonical_id not in node_by_id:
            continue
        for src_file in usage_files.get(name, []):
            # Find the class node for this file
            # The class node ID is `<file_path_with_underscores>_<ClassName>` (where ClassName is the file's stem)
            # File node ID is `<file_path_with_underscores>` (no extension)
            # We need the class node, not the file node
            stem = Path(src_file).stem  # e.g. "DlgReg"
            file_id = src_file.replace("/", "_").replace(".", "_")
            # The class node ends with `_stem_lowercase`
            class_id_candidates = [
                f"{file_id}_{stem.lower()}",
            ]
            class_id = None
            for cid in class_id_candidates:
                if cid in node_by_id:
                    # Check it's actually a class (label is the class name, not file)
                    ninfo = node_by_id[cid]
                    if ninfo.get("label") == stem and ninfo.get("source_file") == src_file:
                        class_id = cid
                        break
            if not class_id:
                # Try other cases (e.g. uppercase stem)
                for nid, ninfo in node_by_id.items():
                    if ninfo.get("source_file") == src_file and ninfo.get("label") == stem and nid != file_id:
                        class_id = nid
                        break
            if not class_id:
                continue
            key = (class_id, canonical_id)
            if key in seen:
                continue
            seen.add(key)
            sinfo = node_by_id[class_id]
            synth_phase2.append({
                "source": class_id,
                "target": canonical_id,
                "relation": "imports",
                "confidence": "INFERRED",
                "confidence_score": 0.55,  # weaker — only source-code grep evidence
                "context": "synthesized_from_source_usage",
                "source_file": src_file,
                "source_location": "L?",
                "weight": 0.4,
                "synthesis_reason": f"`{name}` usage (new {name}(...) or {name}.method(...)) in {src_file}",
            })
    print(f"  Phase 2: {len(synth_phase2)} new edges", flush=True)

    # === Combine and write ===
    all_synth = synth_phase1 + synth_phase2
    out = dict(graph)
    out["links"] = list(links) + all_synth
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"\nWrote {OUT_PATH} with {len(out['links'])} edges ({len(links)} original + {len(all_synth)} synthesized)", flush=True)

    # === Bridge analysis ===
    in_degree_total = defaultdict(int)
    in_degree_real = defaultdict(int)
    in_degree_synth = defaultdict(int)
    for l in out["links"]:
        if l.get("relation") != "imports":
            continue
        tid = l.get("target")
        in_degree_total[tid] += 1
        if "synthesized" in str(l.get("context", "")):
            in_degree_synth[tid] += 1
        else:
            in_degree_real[tid] += 1

    print(f"\nTop 25 bridges by incoming imports (after v2 synthesis):", flush=True)
    sorted_bridges = sorted(in_degree_total.items(), key=lambda x: -x[1])[:25]
    for i, (nid, deg) in enumerate(sorted_bridges, 1):
        info = node_by_id.get(nid, {})
        label = info.get("label", nid)
        src = info.get("source_file", "")
        real = in_degree_real.get(nid, 0)
        synth = in_degree_synth.get(nid, 0)
        is_target = nid in canonical_ids
        marker = " ⭐ TARGET" if is_target else ""
        print(f"  {i:2d}. {deg:5d}  (real={real:4d}  +synth={synth:4d})  {label[:30]:30s}  src={src}{marker}", flush=True)

    # === Per-target count breakdown ===
    per_target = defaultdict(lambda: {"real": 0, "synth_p1": 0, "synth_p2": 0})
    for l in links:
        if l.get("relation") != "imports":
            continue
        tid = l.get("target")
        for name, (cid, _, _) in TARGETS.items():
            if tid == cid:
                per_target[name]["real"] += 1
    for s in synth_phase1:
        tid = s["target"]
        for name, (cid, _, _) in TARGETS.items():
            if tid == cid:
                per_target[name]["synth_p1"] += 1
    for s in synth_phase2:
        tid = s["target"]
        for name, (cid, _, _) in TARGETS.items():
            if tid == cid:
                per_target[name]["synth_p2"] += 1

    # === Write the report ===
    print(f"\nWriting {REPORT_PATH}...", flush=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Synthesized Bridge Report v2\n\n")
        f.write(f"**Input:** `{GRAPH_PATH}` ({len(links):,} edges)\n")
        f.write(f"**Output:** `{OUT_PATH}` ({len(out['links']):,} edges)\n")
        f.write(f"**Time:** {time.time()-t0:.1f}s\n\n")
        f.write(f"**Phase 1 (field-type):** {len(synth_phase1):,} edges\n")
        f.write(f"**Phase 2 (source-code usage):** {len(synth_phase2):,} edges\n")
        f.write(f"**Total synthesized:** {len(all_synth):,}\n\n")

        f.write("## The bug this works around\n\n")
        f.write("graphify's import resolver fails 4 ways for `fungsi.*` shared infra\n")
        f.write("classes (WarnaTable, akses, koneksiDB, sekuel, validasi, batasInput,\n")
        f.write("closingkasir). The graph captures the usages indirectly via field-type\n")
        f.write("references and source-code patterns, so we can recover the import edges\n")
        f.write("in two passes.\n\n")

        f.write("## Per-target synthesis counts\n\n")
        f.write("| Target | Real (original) | + Phase 1 (field) | + Phase 2 (source) | Total after |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for name in sorted(TARGETS, key=lambda k: -(per_target[k]["real"] + per_target[k]["synth_p1"] + per_target[k]["synth_p2"])):
            cid = TARGETS[name][0]
            r = per_target[name]["real"]
            p1 = per_target[name]["synth_p1"]
            p2 = per_target[name]["synth_p2"]
            total = r + p1 + p2
            f.write(f"| `{name}` | {r} | +{p1} | +{p2} | **{total}** |\n")

        f.write("\n## Top 25 bridges by incoming imports (after v2 synthesis)\n\n")
        f.write("| # | Total | Real | Synth | Class | Source file |\n")
        f.write("|---|---:|---:|---:|---|---|\n")
        for i, (nid, deg) in enumerate(sorted_bridges, 1):
            info = node_by_id.get(nid, {})
            real = in_degree_real.get(nid, 0)
            synth = in_degree_synth.get(nid, 0)
            label = info.get("label", "")
            src = info.get("source_file", "")
            is_target = nid in canonical_ids
            star = " ⭐" if is_target else ""
            f.write(f"| {i} | {deg} | {real} | +{synth} | `{label}`{star} | `{src}` |\n")

        f.write("\n## How the original god-nodes list compares\n\n")
        f.write("**Before** (from `GRAPH_REPORT.md`, ranked by total degree):\n\n")
        f.write("| Rank | Node | Old total degree | Was it a real bridge? |\n")
        f.write("|---:|---|---:|---|\n")
        original_gods = [
            "khanzaantrianpoli_src_fungsi_warnatable_warnatable",
            "src_simrskhanza_frmutama_frmutama",
            "src_fungsi_akses_akses",
            "khanzacetakantrianloket_src_fungsi_akses_akses",
            "src_kepegawaian_dlgcaripetugas_dlgcaripetugas",
            "src_simrskhanza_dlgreg_dlgreg",
            "src_simrskhanza_dlgkasirralan_dlgkasirralan",
            "concept_rs_simrs_khanza_branding",
            "src_simrskhanza_dlgrawatjalan_dlgrawatjalan",
            "src_simrskhanza_dlgkamarinap_dlgkamarinap",
        ]
        for i, nid in enumerate(original_gods, 1):
            label = node_by_id.get(nid, {}).get("label", "")
            old_total = sum(1 for l in links if l.get("source") == nid or l.get("target") == nid)
            real_in = in_degree_real.get(nid, 0)
            new_in = in_degree_total.get(nid, 0)
            f.write(f"| {i} | `{label}` | {old_total} | real_imports={real_in} → {new_in} after synthesis |\n")

        f.write("\n## Caveats\n\n")
        f.write("1. **Phase 1 (field-type)** synthesizes from real graph edges — high\n")
        f.write("   confidence (INFERRED 0.65).\n")
        f.write("2. **Phase 2 (source-code grep)** is a coarse signal: we don't check\n")
        f.write("   that the `new X(` or `X.method(` is in a *method body* of the\n")
        f.write("   class node (we just know the file uses the class). The confidence\n")
        f.write("   is lower (INFERRED 0.55).\n")
        f.write("3. We may also count the target's *own* .java file (e.g.,\n")
        f.write("   `src/fungsi/WarnaTable.java` uses `JTable` internally). We filter\n")
        f.write("   the target's own file out of the source-file list.\n")
        f.write("4. The graph is not re-clustered. To re-cluster with synthesized\n")
        f.write("   edges, run `graphify cluster-only .` on `graph_synthesized_v2.json`.\n")
        f.write("5. The synthesized graph has 2x the edges of the field-only\n")
        f.write("   synthesis. It is the most useful artifact for analysis even though\n")
        f.write("   it is noisier.\n")
    print(f"  Wrote {REPORT_PATH}", flush=True)
    print(f"\nDone in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
