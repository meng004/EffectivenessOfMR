"""Join cosmic-ray sessions with function layers and coverage; print per-layer counts.
Usage: python classify.py --cov cov.json a.sqlite [b.sqlite ...] out.csv
shortcut: SQL assumes cosmic-ray 8.x schema; check with `sqlite3 x.sqlite .schema` (doc 3.8)."""
import ast, csv, json, sqlite3, sys
from collections import Counter
from pathlib import Path

args = sys.argv[1:]
cov = json.load(open(args[args.index("--cov") + 1]))["files"] if "--cov" in args else {}
rest = [a for i, a in enumerate(args) if a != "--cov" and (i == 0 or args[i - 1] != "--cov")]
dbs, out = rest[:-1], rest[-1]
layers = {(r["file"], r["function"]): r["layer"] for r in csv.DictReader(open(Path(__file__).parent / "layers.csv"))}


def func_at(path, line):
    """Innermost function/method enclosing a line (by name only)."""
    best = None
    for node in ast.walk(ast.parse(Path(path).read_text())):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno <= line <= node.end_lineno:
            if best is None or node.lineno > best.lineno:
                best = node
    return best.name if best else "<module>"


def covered(path, line):
    for k, v in cov.items():
        if Path(k).name == Path(path).name:
            return int(line in v.get("executed_lines", []))
    return 0


rows = []
for db in dbs:
    q = """SELECT s.module_path, s.operator_name, s.start_pos_row, r.worker_outcome, r.test_outcome, r.output
           FROM mutation_specs s JOIN work_results r ON s.job_id = r.job_id"""
    for path, op, line, wo, to, output in sqlite3.connect(db).execute(q):
        fn = func_at(path, line)
        failed = [ln.split()[1] for ln in (output or "").splitlines() if ln.startswith("MRVERDICT") and ln.endswith("fail")]
        rows.append({"db": Path(db).name, "file": Path(path).name, "line": line, "function": fn,
                     "layer": layers.get((Path(path).name, fn), "unlabeled"), "operator": op,
                     "covered": covered(path, line), "worker": str(wo).split(".")[-1].lower(),
                     "test": str(to).split(".")[-1].lower(), "failed_mrs": ";".join(failed)})

with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["db"])
    w.writeheader(); w.writerows(rows)

usable = Counter(r["layer"] for r in rows
                 if r["covered"] and r["worker"] == "normal" and r["test"] in ("killed", "survived"))
print("total", len(rows), "usable_by_layer", dict(usable))
for layer in ("equation", "non_equation"):
    print(layer, "PASS" if usable[layer] >= 30 else "FAIL", usable[layer])
