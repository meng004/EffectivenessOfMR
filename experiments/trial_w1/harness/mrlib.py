"""Shared helpers. Nuclide order fixed: chain1 = 0..2, chain2 = 3..5."""
import math
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
NAMES = ["I135", "Xe135", "Cs135", "Sr90", "Y90", "Zr90"]
HALF = {"I135": 23688.0, "Xe135": 32904.0, "Sr90": 908523000.0, "Y90": 230400.0}
DAY = 86400.0
RTOL = 1e-10  # frozen after healthy baseline (design doc 3.4)
CHAIN1, CHAIN2 = [0, 1, 2], [3, 4, 5]


def build_A_ref():
    """Independent hand-written decay matrix; never touches OpenMC code."""
    A = np.zeros((6, 6))
    for i, n in enumerate(NAMES):
        if n in HALF:
            lam = math.log(2) / HALF[n]
            A[i, i] -= lam
            A[i + 1, i] += lam  # each decays to the next nuclide in its chain
    return A


def build_A_openmc():
    """Matrix assembled by OpenMC's own Chain code (mutation target chain.py/nuclide.py).
    shortcut: zero reaction rates assumed accepted by form_matrix; verify v0.15.2 API (doc 3.2)."""
    from openmc.deplete import Chain
    from openmc.deplete.reaction_rates import ReactionRates
    chain = Chain.from_xml(str(HERE / "toy_chain.xml"))
    names = [n.name for n in chain.nuclides]
    rates = ReactionRates(["0"], names, [])
    A = chain.form_matrix(rates[0]).toarray()
    idx = [names.index(n) for n in NAMES]
    return A[np.ix_(idx, idx)]


def solve(A, n0, dt):
    from scipy.sparse import csc_matrix
    from openmc.deplete.cram import CRAM48
    return np.asarray(CRAM48(csc_matrix(A), np.asarray(n0, float), dt))


def n0_default():
    n = np.zeros(6)
    n[0] = n[3] = 1e20
    return n


def close(a, b, rtol=RTOL):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(np.all(np.abs(a - b) <= rtol * max(np.max(np.abs(b)), 1.0)))
