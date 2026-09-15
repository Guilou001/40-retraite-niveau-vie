"""Oracles numériques indépendants du programme de recherche."""

import numpy as np
import pandas as pd
import pytest

from rnv.experiment import historical_windows
from rnv.model import Policy, measure, simulate
from rnv.support import block_indices


@pytest.mark.parametrize("second, expected", [(0.10, 42000), (-0.10, 39400)])
def test_vanguard_figure_six(second, expected):
    # Vanguard (2021), figure 6, capital initial d'un million, frais nuls.
    paid, wealth, _ = simulate([0, second], [0, 0], "dynamic", Policy(fee=0))
    np.testing.assert_allclose(paid, [[40000, expected]])
    assert wealth[0, 1] == pytest.approx(960000 * (1 + second) - expected)


def test_exact_inflation_and_fee_accounting():
    p = Policy(initial=1000, rate=0.04, fee=0.01)
    paid, wealth, _ = simulate([0.10], [0.05], "fixed", p)
    assert paid[0, 0] == 40
    assert wealth[0, 0] == pytest.approx(1000 * 1.10 * 0.99 / 1.05 - 40)


def test_sequence_matters_with_same_compounded_return():
    a = simulate([-0.2, 0.25], [0, 0], "fixed", Policy(initial=100, rate=0.1, fee=0))[1][0, -1]
    b = simulate([0.25, -0.2], [0, 0], "fixed", Policy(initial=100, rate=0.1, fee=0))[1][0, -1]
    assert a == pytest.approx(77.5)
    assert b == pytest.approx(82)


def test_ruin_pays_only_remaining_balance_and_stays_zero():
    paid, wealth, missing = simulate([0, 0, 0], [0, 0, 0], "fixed", Policy(initial=100, rate=0.6, fee=0))
    np.testing.assert_allclose(paid, [[60, 40, 0]])
    np.testing.assert_allclose(wealth, [[40, 0, 0]])
    assert missing.tolist() == [[False, True, True]]


def test_budget_shortfall_is_possible_without_ruin():
    p = Policy(initial=100, rate=0.04, fee=0)
    outputs = simulate([0, -0.5, 0], [0, 0, 0], "percentage", p)
    m = measure(*outputs, p)
    assert not m.ruined.iloc[0]
    assert m.below_budget.iloc[0]
    assert m.longest_shortfall.iloc[0] == 2


def test_floor_limits_cuts_but_does_not_create_money():
    p = Policy(initial=100, rate=0.04, fee=0)
    paid, wealth, _ = simulate([0, -0.999, 0], [0, 0, 0], "floor", p)
    assert paid[0, 1] == pytest.approx(0.096)
    assert wealth[0, 1] == 0


def test_vectorization_matches_paths_separately():
    r = np.array([[0.1, -0.2, 0.3], [-0.2, 0.4, 0.01]])
    pi = np.array([[0.02, 0.01, -0.01], [0.1, 0.01, 0.03]])
    for rule in ["fixed", "percentage", "dynamic", "floor"]:
        together = simulate(r, pi, rule)
        for i in range(2):
            separate = simulate(r[i], pi[i], rule)
            for a, b in zip(together, separate, strict=True):
                np.testing.assert_allclose(a[i], b[0])


def test_missing_year_is_not_silently_bridged():
    data = pd.DataFrame({"year": [2000, 2001, 2003], "portfolio": [0, 0, 0], "inflation": [0, 0, 0]})
    starts, _, _ = historical_windows(data, 3)
    assert starts == []


def test_blocks_preserve_consecutive_years():
    idx = block_indices(20, 5, 10, 3, np.random.default_rng(1))
    assert idx.shape == (5, 10)
    for start in [0, 3, 6]:
        np.testing.assert_array_equal((idx[:, start + 1] - idx[:, start]) % 20, 1)


@pytest.mark.parametrize("r,pi", [([np.nan], [0]), ([0], [-1]), ([-1.01], [0])])
def test_invalid_observations_rejected(r, pi):
    with pytest.raises(ValueError):
        simulate(r, pi, "fixed")
