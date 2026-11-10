"""MR verdict: exit 0 if all 5 MRs pass (mutant survives), 1 otherwise (killed)."""
import sys
import numpy as np
import mrlib as m


def mrs():
    A, d = m.build_A_openmc(), m.DAY
    n0 = m.n0_default()
    f = lambda n, t=d: m.solve(A, n, t)
    base = f(n0)
    a, b = np.zeros(6), np.zeros(6)
    a[0], b[3] = 1e20, 1e20
    yield "MR1_linear", m.close(f(2 * n0), 2 * base)
    yield "MR2_superpose", m.close(f(a) + f(b), base)
    yield "MR3_semigroup", m.close(f(f(n0), d), f(n0, 2 * d))
    yield "MR4_conserve", all(m.close(base[c].sum(), n0[c].sum()) for c in (m.CHAIN1, m.CHAIN2))
    yield "MR5_zero_block", m.close(f(a)[m.CHAIN2], np.zeros(3))


if __name__ == "__main__":
    ok = True
    try:
        for name, passed in mrs():
            print("MRVERDICT", name, "pass" if passed else "fail")
            ok &= passed
    except Exception as e:  # crash under mutation counts as detected
        print("MRVERDICT crash", type(e).__name__)
        ok = False
    sys.exit(0 if ok else 1)
