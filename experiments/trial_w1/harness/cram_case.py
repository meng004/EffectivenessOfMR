"""Item 1: run the CRAM toy case, write output hash and wall time to JSON."""
import hashlib, json, sys, time
import numpy as np
import mrlib

t0 = time.perf_counter()
A = mrlib.build_A_openmc()
n = mrlib.solve(A, mrlib.n0_default(), mrlib.DAY)
sec = time.perf_counter() - t0
out = {"n": n.tolist(), "seconds": round(sec, 3),
       "sha256": hashlib.sha256(np.ascontiguousarray(n).tobytes()).hexdigest()}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(out["sha256"], out["seconds"])
