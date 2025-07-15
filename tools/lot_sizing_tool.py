#!/usr/bin/env python3
"""lot_sizing_tool.py — deterministic single-item lot-sizing via Gurobi
============================================================================
This module exposes **two SmolAgents tools**:

* ``solve_lot_sizing``     → returns a *dict* (plan, inventory, setup flags & cost)
* ``solve_lot_sizing_basic`` → returns *(production_plan, total_cost)* for quick use

The docstrings are written in **Google style** so SmolAgents ≥ 1.18 can build
JSON schemas automatically.

Usage from shell (JSON stdin → JSON stdout)  ────────────────────────────────

```bash
echo '{"demand":[100,150,80,130],"setup_cost":1000,"unit_cost":50,"holding_cost":2}' | \
  python tools/lot_sizing_tool.py
```

Prerequisites
-------------
* A working **Gurobi** installation & licence (Academic licence is OK).
* ``pip install --extra-index-url https://pypi.gurobi.com gurobipy``
* ``pip install smolagents gurobipy-stubs`` (stubs optional, for IntelliSense).
"""
from __future__ import annotations

from typing import List, Dict, Tuple
import json, sys, gurobipy as gp  # type: ignore
from gurobipy import GRB  # type: ignore
from smolagents import tool

# ────────────────────────────────────────────────────────────────────────────
# Internal helper – solves the MILP and returns raw vectors + cost
# ────────────────────────────────────────────────────────────────────────────


def _solve_core(
    demand: List[float],
    setup_cost: float,
    unit_cost: float,
    holding_cost: float,
    initial_inventory: float,
) -> Tuple[List[float], List[float], List[int], float]:
    """Run the Wagner-Whitin MILP in Gurobi and return raw components."""

    T = len(demand)
    m = gp.Model("lot_sizing")
    m.Params.OutputFlag = 0  # silent

    prod = m.addVars(T, lb=0.0, name="prod")
    inv = m.addVars(T, lb=0.0, name="inv")
    y = m.addVars(T, vtype=GRB.BINARY, name="setup")

    bigM = sum(demand) + initial_inventory

    for t in range(T):
        prev_inv = initial_inventory if t == 0 else inv[t - 1]
        m.addConstr(prev_inv + prod[t] - demand[t] == inv[t], name=f"bal_{t}")
        m.addConstr(prod[t] <= bigM * y[t], name=f"link_{t}")

    cost = (
        setup_cost * gp.quicksum(y)
        + unit_cost * gp.quicksum(prod)
        + holding_cost * gp.quicksum(inv)
    )
    m.setObjective(cost, GRB.MINIMIZE)
    m.optimize()

    if m.Status != GRB.OPTIMAL:
        raise RuntimeError(f"Gurobi status {m.Status}: optimisation failed")

    return (
        [prod[t].X for t in range(T)],
        [inv[t].X for t in range(T)],
        [int(round(y[t].X)) for t in range(T)],
        m.ObjVal,
    )


# ────────────────────────────────────────────────────────────────────────────
# Public SmolAgents tools
# ────────────────────────────────────────────────────────────────────────────


@tool
def solve_lot_sizing(
    demand: List[float],
    setup_cost: float,
    unit_cost: float,
    holding_cost: float,
    initial_inventory: float = 0.0,
) -> Dict[str, List[float] | float]:
    """Compute the optimal lot-sizing plan and return a *dictionary*.

    Args:
        demand: Demand quantity for each period (length *T*).
        setup_cost: Fixed cost incurred whenever production occurs in a period.
        unit_cost: Variable production cost per unit produced.
        holding_cost: Inventory carrying cost per unit per period.
        initial_inventory: On-hand stock before period 1. Defaults to ``0``.

    Returns:
        Dict with four keys:
            ``production_plan`` – list[float], qty produced each period.
            ``inventory`` – list[float], ending inventory each period.
            ``setup`` – list[int], 0/1 flag if production occurs in period.
            ``total_cost`` – float, optimal objective value.
    """
    plan, inv, setups, cost = _solve_core(
        demand, setup_cost, unit_cost, holding_cost, initial_inventory
    )
    return {
        "production_plan": plan,
        "inventory": inv,
        "setup": setups,
        "total_cost": cost,
    }


@tool
def solve_lot_sizing_basic(
    demand: List[float],
    setup_cost: float,
    unit_cost: float,
    holding_cost: float,
    initial_inventory: float = 0.0,
) -> Tuple[List[float], float]:
    """Return *(production_plan, total_cost)* for easy unpacking.

    Args:
        demand: Demand quantity for every period.
        setup_cost: Fixed setup cost per production run.
        unit_cost: Variable cost per unit produced.
        holding_cost: Cost per unit of inventory held per period.
        initial_inventory: Initial stock before period 1.

    Returns:
        Tuple containing
            • list[float] production plan
            • float total cost
    """
    plan, _inv, _setup, cost = _solve_core(
        demand, setup_cost, unit_cost, holding_cost, initial_inventory
    )
    return plan, cost


# ────────────────────────────────────────────────────────────────────────────
# Command-line entry – read JSON stdin, write JSON stdout
# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = solve_lot_sizing(**data)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
