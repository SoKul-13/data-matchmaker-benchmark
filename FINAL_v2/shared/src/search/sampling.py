"""
Candidate designs on the probability simplex (weights >= 0, sum = 1), all on the same step lattice.

  simplex_grid(K, step)              every lattice point (stars and bars); exact for small K
  sample_uniform_lattice(n, K, step) n distinct lattice points drawn uniformly without replacement (v2 / v3 design)
  sample_dirichlet_lattice(n, K, step) n distinct points: Dirichlet(1) draws snapped to the lattice (v4 design)
  sample_lhs_simplex(n, K, step)     Latin hypercube design on the simplex: K stratified uniforms -> exponential inverse CDF
                                     -> normalise (uniform on the simplex, each marginal stratified into n bins), then snapped
                                     to the lattice; duplicates are re-drawn from a fresh permutation of the same strata
  coverage(W)                        design diagnostics: minimum pairwise L1 distance, mean nearest-neighbour distance,
                                     centred L2 discrepancy of the first K-1 coordinates, per-coordinate range coverage

McKay, Beckman & Conover (1979) for Latin hypercube sampling; the exponential-spacings map is the standard way to make the
LHS uniform on the simplex (each coordinate of a Dirichlet(1,...,1) vector is an exponential spacing normalised by the sum).
"""
from __future__ import annotations

import itertools
from typing import Dict

import numpy as np


def simplex_grid(K: int, step: float) -> np.ndarray:
    units = int(round(1 / step)); out = []
    for cuts in itertools.combinations(range(units + K - 1), K - 1):
        prev, comp = -1, []
        for c in cuts:
            comp.append(c - prev - 1); prev = c
        comp.append(units + K - 2 - prev); out.append(comp)
    return np.asarray(out, float) / units


def n_lattice_points(K: int, step: float) -> int:
    from math import comb
    units = int(round(1 / step)); return comb(units + K - 1, K - 1)


def snap_to_lattice(P: np.ndarray, step: float) -> np.ndarray:
    """largest-remainder rounding so every row stays on the lattice and sums to exactly 1"""
    units = int(round(1 / step)); out = np.empty_like(P)
    for i, p in enumerate(P):
        c = np.floor(p * units).astype(int)
        for _ in range(units - c.sum()):
            c[np.argmax(p * units - c)] += 1
        out[i] = c / units
    return out


def _dedupe(rows, seen, step):
    units = int(round(1 / step)); keep = []
    for r in rows:
        key = tuple(np.round(r * units).astype(int))
        if key not in seen:
            seen.add(key); keep.append(r)
    return keep


def sample_uniform_lattice(n: int, K: int, step: float, seed: int = 0) -> np.ndarray:
    G = simplex_grid(K, step); rng = np.random.default_rng(seed)
    return G[rng.choice(len(G), min(n, len(G)), replace=False)]


def sample_dirichlet_lattice(n: int, K: int, step: float, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed); seen, out = set(), []
    while len(out) < n:
        out += _dedupe(snap_to_lattice(rng.dirichlet(np.ones(K), size=n), step), seen, step)
    return np.asarray(out[:n])


def lhs_unit_cube(n: int, K: int, rng: np.random.Generator) -> np.ndarray:
    """n x K Latin hypercube: each column is a random permutation of the n strata with a uniform jitter inside the stratum"""
    U = np.empty((n, K))
    for k in range(K):
        U[:, k] = (rng.permutation(n) + rng.uniform(size=n)) / n
    return U


def sample_lhs_simplex(n: int, K: int, step: float | None = None, seed: int = 0, max_rounds: int = 50) -> np.ndarray:
    """Latin hypercube on the simplex.  U (n x K) stratified uniforms -> E = -ln(1 - U) (exponential spacings) -> W = E / E.sum(1).
    If `step` is given the points are snapped to the lattice; duplicates created by snapping are replaced by points from a fresh
    LHS round so the design keeps n distinct points."""
    rng = np.random.default_rng(seed); seen, out = set(), []
    for _ in range(max_rounds):
        E = -np.log(1.0 - lhs_unit_cube(n, K, rng)); W = E / E.sum(1, keepdims=True)
        if step is None:
            return W
        out += _dedupe(snap_to_lattice(W, step), seen, step)
        if len(out) >= n:
            break
    return np.asarray(out[:n])


def coverage(W: np.ndarray) -> Dict[str, float]:
    """Design diagnostics.  Distances in L1 on the simplex; discrepancy on the first K-1 coordinates (the last is determined)."""
    W = np.asarray(W, float); n, K = W.shape
    D = np.abs(W[:, None, :] - W[None, :, :]).sum(-1); np.fill_diagonal(D, np.inf)
    nn = D.min(1)
    X = W[:, : K - 1]
    # centred L2 discrepancy (Hickernell 1998)
    a = np.prod(1 + 0.5 * np.abs(X - 0.5) - 0.5 * (X - 0.5) ** 2, axis=1)
    b = np.prod(1 + 0.5 * np.abs(X[:, None, :] - 0.5) + 0.5 * np.abs(X[None, :, :] - 0.5) - 0.5 * np.abs(X[:, None, :] - X[None, :, :]), axis=2)
    cl2 = (13 / 12) ** (K - 1) - 2 / n * a.sum() + 1 / n ** 2 * b.sum()
    rng_cov = float(np.mean([(np.unique(np.round(W[:, k], 6)).size) for k in range(K)]))
    return {"n": int(n), "K": int(K), "min_pairwise_L1": float(nn.min()), "mean_nearest_L1": float(nn.mean()),
            "centred_L2_discrepancy": float(np.sqrt(max(cl2, 0.0))), "mean_distinct_values_per_weight": rng_cov,
            "share_with_a_zero_weight": float(np.mean((W <= 1e-12).any(1)))}


def design_table(K: int, step: float, n: int, seed: int) -> Dict[str, np.ndarray]:
    """the three designs at the same budget; exhaustive if the lattice is small enough"""
    out = {"uniform_lattice": sample_uniform_lattice(n, K, step, seed), "dirichlet_lattice": sample_dirichlet_lattice(n, K, step, seed),
           "lhs_simplex": sample_lhs_simplex(n, K, step, seed)}
    if n_lattice_points(K, step) <= 50_000:
        out["exhaustive"] = simplex_grid(K, step)
    return out
