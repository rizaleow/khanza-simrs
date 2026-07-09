"""
Post-process graph.json to synthesize missing import edges for shared infra classes.

Background: graphify's import resolver mis-routes or drops imports for `fungsi.*`
classes (WarnaTable, akses, koneksiDB, sekuel, validasi, batasInput, closingkasir).
The graph DOES capture these classes being used as field types via `references field`
edges to `<file>_java_<fieldname>` field-ref nodes. This script synthesizes
`imports` edges from each dialog class to the matching shared infra class.

Output: a new graph.json (or appended JSON) with synthesized edges marked
INFERRED + AMBIGUOUS so the bridge analysis can recover the real central classes.
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

GRAPH_PATH = "graphify-out/graph.json"
OUT_PATH = "graphify-out/graph_synthesized.json"
REPORT_PATH = "graphify-out/SYNTHESIZED_REPORT.md"

# Class names we want to prioritize matching. The canonical `src/fungsi/*` shared
# infra has these names (and these have been confirmed to have 0 incoming imports).
TARGET_NAMES = {
    # name -> (canonical id, source_file, description)
    "WarnaTable":   ("src_fungsi_warnatable_warnatable", "src/fungsi/WarnaTable.java", "JTable zebra-striping renderer (canonical)"),
    "akses":        ("src_fungsi_akses_akses", "src/fungsi/akses.java", "Auth / user session"),
    "koneksiDB":    ("src_fungsi_koneksidb_koneksidb", "src/fungsi/koneksiDB.java", "DB connection factory"),
    "sekuel":       ("src_fungsi_sekuel_sekuel", "src/fungsi/sekuel.java", "SQL execution wrapper"),
    "validasi":     ("src_fungsi_validasi_validasi", "src/fungsi/validasi.java", "Input validation helpers"),
    "batasInput":   ("src_fungsi_batasinput_batasinput", "src/fungsi/batasInput.java", "JTextField max-length wrapper"),
    "WarnaTable2":  ("src_fungsi_warnatable2_warnatable2", "src/fungsi/WarnaTable2.java", "JTable zebra-striping v2"),
    "WarnaTable3":  ("src_fungsi_warnatable3_warnatable3", "src/fungsi/WarnaTable3.java", "JTable zebra-striping v3"),
    "WarnaTable4":  ("src_fungsi_warnatable4_warnatable4", "src/fungsi/WarnaTable4.java", "JTable zebra-striping v4"),
    "WarnaTable5":  ("src_fungsi_warnatable5_warnatable5", "src/fungsi/WarnaTable5.java", "JTable zebra-striping v5"),
    "cacheregistrasi":  ("src_fungsi_cacheregistrasi", "src/fungsi/cacheregistrasi.java", "Registration cache"),
    "catatanpasien":    ("src_fungsi_catatanpasien", "src/fungsi/catatanpasien.java", "Patient notes wrapper"),
    "closingkasir":     ("src_fungsi_closingkasir", "src/fungsi/closingkasir.java", "End-of-day cashier close"),
}

# Names we should NEVER synthesize (Java standard library, Swing, etc.)
EXTERNAL_NAMES = {
    "String", "Integer", "Long", "Boolean", "Byte", "Double", "Float", "Short",
    "Object", "Class", "Throwable", "Exception", "RuntimeException",
    "Connection", "PreparedStatement", "ResultSet", "Statement", "DriverManager",
    "JButton", "JLabel", "JTextField", "JTextArea", "JTable", "JPanel", "JFrame",
    "JDialog", "JMenu", "JMenuItem", "JCheckBox", "JRadioButton", "JComboBox",
    "JScrollPane", "JTabbedPane", "JTree", "JList", "JFileChooser", "JOptionPane",
    "JProgressBar", "JSpinner", "JSlider", "JToggleButton", "JSeparator",
    "JInternalFrame", "JDesktopPane", "JLayeredPane", "JRootPane", "JPopupMenu",
    "JToolBar", "JMenuBar", "Button", "Label", "TextBox", "ComboBox", "CekBox",
    "Table", "ScrollPane", "TextArea", "PasswordBox", "ButtonBig", "panelisi",
    "Tanggal", "PanelGlass", "Separator", "DefaultTableModel", "TableColumn",
    "ImageIcon", "Icon", "Color", "Font", "Dimension", "Point", "Rectangle",
    "Cursor", "Component", "Container", "Window", "Frame", "Dialog",
    "KeyEvent", "MouseEvent", "WindowEvent", "ActionEvent", "ActionListener",
    "KeyListener", "MouseListener", "WindowListener", "ComponentListener",
    "FocusListener", "DocumentListener", "CaretListener", "ListSelectionListener",
    "PropertyChangeListener", "ChangeListener", "ItemListener", "TableModel",
    "TableModelEvent", "ListSelectionEvent", "TreeSelectionEvent",
    "HttpClient", "HttpEntity", "HttpHeaders", "HttpRequest", "HttpResponse",
    "URL", "URI", "File", "FileReader", "FileWriter", "BufferedReader",
    "InputStream", "OutputStream", "Reader", "Writer", "IOException",
    "SimpleDateFormat", "Calendar", "Date", "Timestamp", "Time",
    "HashMap", "HashSet", "TreeMap", "TreeSet", "ArrayList", "LinkedList",
    "List", "Map", "Set", "Collection", "Iterator", "ListIterator",
    "Pattern", "Matcher", "StringBuilder", "StringBuffer",
    "JsonNode", "ObjectMapper", "ObjectReader", "ObjectWriter",
    "BigDecimal", "BigInteger", "Number",
    "AES", "SecretKey", "KeyGenerator", "Cipher",
    "Socket", "ServerSocket", "InetAddress", "URLConnection",
    "Process", "Runtime", "System", "Thread",
    "ComponentUI", "LookAndFeel", "UIManager", "UIDefaults",
    "GetMethod", "PostMethod", "HttpClient", "Header", "HeaderGroup",
    "SuppressWarnings", "Override", "Deprecated",
    "this", "super", "null", "true", "false",
    "var", "let", "const", "function", "class", "import", "export",
    "ObjectInputStream", "ObjectOutputStream", "Serializable", "Externalizable",
}


def main():
    t0 = time.time()
    print("Loading graph...", flush=True)
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)

    nodes = graph["nodes"]
    links = graph["links"]
    node_by_id = {n["id"]: n for n in nodes}

    # Build set of valid canonical class node IDs (only src/fungsi/ canonical, plus
    # any other class that's unique in the corpus)
    canonical_ids = {v[0] for v in TARGET_NAMES.values()}
    # Verify they exist
    for cid in canonical_ids:
        if cid not in node_by_id:
            print(f"WARNING: canonical class {cid} not in graph (skipping)", flush=True)

    # For each target name, find all nodes with that label (could be class, field-ref, etc.)
    # so we know how many candidates exist
    label_to_ids = defaultdict(list)
    for nid, n in node_by_id.items():
        lbl = n.get("label", "")
        if lbl and not lbl.startswith(".") and not lbl.endswith(".java"):
            label_to_ids[lbl].append(nid)
    print(f"  {len(label_to_ids)} unique labels", flush=True)

    # For the target names, list all matching node IDs
    print("\nTarget name candidates in corpus:", flush=True)
    for name in TARGET_NAMES:
        candidates = label_to_ids.get(name, [])
        canonical = TARGET_NAMES[name][0]
        in_canonical = canonical in candidates
        print(f"  {name:18s}  {len(candidates):3d} candidates  canonical_present={in_canonical}", flush=True)

    # Find all `references field` edges from a CLASS node to a field-ref node
    # The class node ID ends with `_<ClassName>`, no `_java_` in it
    # The field-ref ID has `_java_` in it
    print("\nScanning `references field` edges...", flush=True)
    field_edges = []
    for l in links:
        if l.get("relation") != "references":
            continue
        if l.get("context") != "field":
            continue
        sid = l.get("source")
        tid = l.get("target")
        # Source must be a class node (ends in _ClassName with no _java_)
        # Target must be a field-ref node (contains _java_)
        if "_java_" not in tid:
            continue
        # Confirm target is a field-ref
        tinfo = node_by_id.get(tid, {})
        if tinfo.get("label", "").startswith("."):
            continue
        field_edges.append(l)

    print(f"  {len(field_edges)} `references field` edges to field-ref nodes", flush=True)

    # For each, get field name = label of the field-ref target
    # Then find canonical class with that name
    synthesized = []
    skipped = []
    per_target_count = defaultdict(int)
    per_source_count = defaultdict(int)
    seen_synth = set()  # to dedupe

    for l in field_edges:
        sid = l.get("source")  # class node id
        tid = l.get("target")  # field-ref node id
        tinfo = node_by_id.get(tid, {})
        field_name = tinfo.get("label", "")
        if not field_name or field_name in EXTERNAL_NAMES:
            continue
        if field_name not in TARGET_NAMES:
            continue
        target_id, target_src, desc = TARGET_NAMES[field_name]
        if target_id not in node_by_id:
            continue

        # Dedup
        key = (sid, target_id)
        if key in seen_synth:
            continue
        seen_synth.add(key)

        # Synthesize import edge
        # Find source_file of the field-ref (that's where the field is declared)
        # Note: the field-ref node has no source_file (it's a type ref)
        # We use the source_file of the source class node
        sinfo = node_by_id.get(sid, {})
        synthesized.append({
            "source": sid,
            "target": target_id,
            "relation": "imports",
            "confidence": "INFERRED",
            "confidence_score": 0.65,
            "context": "synthesized_from_field_type",
            "source_file": sinfo.get("source_file", ""),
            "source_location": l.get("source_location", ""),
            "weight": 0.5,
            "synthesis_reason": f"field type `{field_name}` at {sinfo.get('source_file','')}:{l.get('source_location','')} matches canonical `fungsi.{field_name}` in {target_src}",
        })
        per_target_count[field_name] += 1
        per_source_count[sid] += 1

    print(f"\nSynthesized {len(synthesized)} import edges (INFERRED 0.65, marked synthesized)", flush=True)
    print("\nPer-target counts (how many new importers each canonical class gains):", flush=True)
    for name in sorted(per_target_count, key=lambda k: -per_target_count[k]):
        new_count = per_target_count[name]
        canonical_id = TARGET_NAMES[name][0]
        existing = sum(1 for l in links if l.get("target") == canonical_id and l.get("relation") == "imports")
        print(f"  {name:18s}  existing_imports={existing:4d}  +synthesized={new_count:4d}  total={existing+new_count:4d}", flush=True)

    # Write synthesized graph
    print(f"\nWriting {OUT_PATH}...", flush=True)
    out = dict(graph)
    out["links"] = list(links) + synthesized
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"  Wrote {len(out['links'])} edges ({len(links)} original + {len(synthesized)} synthesized)", flush=True)

    # Build bridge analysis on the synthesized graph
    print(f"\nBuilding bridge analysis...", flush=True)
    in_degree = defaultdict(int)
    in_degree_real = defaultdict(int)  # excluding synthesized
    in_degree_synth = defaultdict(int)  # only synthesized
    for l in out["links"]:
        if l.get("relation") != "imports":
            continue
        tid = l.get("target")
        in_degree[tid] += 1
        if l.get("context") == "synthesized_from_field_type":
            in_degree_synth[tid] += 1
        else:
            in_degree_real[tid] += 1

    # Top 20 by total in-degree
    print(f"\nTop 20 bridge nodes by incoming imports (after synthesis):", flush=True)
    sorted_bridges = sorted(in_degree.items(), key=lambda x: -x[1])[:20]
    for nid, deg in sorted_bridges:
        info = node_by_id.get(nid, {})
        label = info.get("label", nid)
        src = info.get("source_file", "")
        real = in_degree_real.get(nid, 0)
        synth = in_degree_synth.get(nid, 0)
        is_target = nid in canonical_ids
        marker = " ← TARGET" if is_target else ""
        print(f"  {deg:5d}  (real={real:4d}  +synth={synth:4d})  {nid[:60]:60s}  src={src}  label={label}{marker}", flush=True)

    # Write the report
    print(f"\nWriting {REPORT_PATH}...", flush=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Synthesized Bridge Report\n\n")
        f.write(f"**Input:** `{GRAPH_PATH}` ({len(links):,} edges)\n")
        f.write(f"**Output:** `{OUT_PATH}` ({len(out['links']):,} edges = {len(links):,} original + {len(synthesized):,} synthesized)\n")
        f.write(f"**Time:** {time.time()-t0:.1f}s\n\n")

        f.write("## What this script does\n\n")
        f.write("The graphify import resolver mis-routes or drops imports for `fungsi.*` shared\n")
        f.write("infra classes (WarnaTable, akses, koneksiDB, sekuel, validasi, batasInput,\n")
        f.write("closingkasir). The graph *does* capture these classes being used as field\n")
        f.write("types via `references field` edges to `<file>_java_<fieldname>` field-ref\n")
        f.write("nodes. This script synthesizes `imports` edges from each dialog class to\n")
        f.write("the matching canonical `src/fungsi/*` class based on the field type.\n\n")
        f.write("Synthesized edges are marked:\n")
        f.write("- `relation`: `imports`\n")
        f.write("- `confidence`: `INFERRED`\n")
        f.write("- `confidence_score`: 0.65 (weak inference, no shape evidence — only field-type match)\n")
        f.write("- `context`: `synthesized_from_field_type`\n")
        f.write("- `weight`: 0.5 (treat as soft signal, half of EXTRACTED)\n\n")
        f.write("## Per-target synthesis counts\n\n")
        f.write("| Target | Existing imports | + Synthesized | Total after |\n")
        f.write("|---|---:|---:|---:|\n")
        for name in sorted(TARGET_NAMES, key=lambda k: -per_target_count.get(k, 0)):
            canonical_id = TARGET_NAMES[name][0]
            existing = sum(1 for l in links if l.get("target") == canonical_id and l.get("relation") == "imports")
            new = per_target_count.get(name, 0)
            f.write(f"| `{name}` ({canonical_id}) | {existing} | +{new} | **{existing+new}** |\n")

        f.write("\n## Top 25 bridges by incoming imports (after synthesis)\n\n")
        f.write("| # | Total | Real | Synth | Class | Source file |\n")
        f.write("|---|---:|---:|---:|---|---|\n")
        for i, (nid, deg) in enumerate(sorted(in_degree.items(), key=lambda x: -x[1])[:25], 1):
            info = node_by_id.get(nid, {})
            real = in_degree_real.get(nid, 0)
            synth = in_degree_synth.get(nid, 0)
            label = info.get("label", "")
            src = info.get("source_file", "")
            is_target = nid in canonical_ids
            star = " ⭐" if is_target else ""
            f.write(f"| {i} | {deg} | {real} | +{synth} | `{label}`{star} | `{src}` |\n")

        f.write("\n## Bridge score: synthesized vs original god-nodes\n\n")
        f.write("The original `GRAPH_REPORT.md` god-nodes list ranked these 10 nodes\n")
        f.write("by *total* degree (mostly `method` self-declarations):\n\n")
        f.write("| Original rank | Node | Old degree | Old in-degree (real) | New in-degree (after synthesis) |\n")
        f.write("|---:|---|---:|---:|---:|\n")
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
            old_total = sum(1 for l in links if l.get("source") == nid or l.get("target") == nid)
            old_in = in_degree_real.get(nid, 0) + sum(
                1 for l in links
                if l.get("target") == nid
                and l.get("relation") in ("imports", "references", "calls", "inherits")
                and l.get("context") != "synthesized_from_field_type"
            )
            new_in = sum(
                1 for l in out["links"]
                if l.get("target") == nid
                and l.get("relation") in ("imports", "references", "calls", "inherits")
            )
            f.write(f"| {i} | `{nid}` | {old_total} | {old_in} | **{new_in}** |\n")

        f.write("\n## How to use the synthesized graph\n\n")
        f.write("The synthesized edges are flagged with `context: synthesized_from_field_type`\n")
        f.write("and `confidence_score: 0.65`. To use them in analysis:\n\n")
        f.write("- **For 'which dialogs depend on X' queries:** include synthesized edges\n")
        f.write("  (`confidence_score >= 0.6` filters EXTRACTED + synthesized INFERRED)\n")
        f.write("- **For 'is this a true god node' questions:** require `confidence_score = 1.0`\n")
        f.write("  (only EXTRACTED)\n")
        f.write("- **For 'which dialogs definitely use X' audit:** require EXTRACTED only\n")
        f.write("  and accept that the true count is higher (synthesized is the floor estimate)\n\n")
        f.write("## Caveats\n\n")
        f.write("1. The synthesis is based on field-type matches. If a dialog uses a\n")
        f.write("   `fungsi.X` class WITHOUT declaring it as a field (e.g., as a static\n")
        f.write("   singleton like `akses.getform()`), the import won't be synthesized\n")
        f.write("   because there's no field reference. This is the *most-called* case\n")
        f.write("   for `akses` (602 call sites in DlgReg.java alone) — those still won't\n")
        f.write("   show up unless you run the graphify resolver fix.\n")
        f.write("2. The synthesis picks the *first* canonical class with a matching label.\n")
        f.write("   For `WarnaTable` (5 variants) this picks the canonical `WarnaTable`,\n")
        f.write("   not the 2/3/4/5 variants. That's a deliberate choice — the canonical\n")
        f.write("   is the workhorse per the project CLAUDE.md.\n")
        f.write("3. The graph is not re-clustered. Communities are unchanged from the\n")
        f.write("   original. To recompute communities after synthesis, re-run\n")
        f.write("   `graphify cluster-only .` on the synthesized graph.\n")
    print(f"  Wrote {REPORT_PATH}", flush=True)
    print(f"\nDone in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
