"""Reference oracle: OpenMC pipeline vs scipy expm on the independent hand-written matrix."""
import sys
from scipy.linalg import expm
import mrlib as m

try:
    got = m.solve(m.build_A_openmc(), m.n0_default(), m.DAY)
    ref = expm(m.build_A_ref() * m.DAY) @ m.n0_default()
    ok = m.close(got, ref, rtol=1e-8)  # CRAM48 accuracy, not the MR tolerance
except Exception as e:
    print("ORACLE crash", type(e).__name__)
    ok = False
print("ORACLE", "pass" if ok else "fail")
sys.exit(0 if ok else 1)
