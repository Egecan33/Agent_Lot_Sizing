#!/usr/bin/env python3
"""cap_lot_sizing_tool.py — *capacitated* deterministic lot-sizing
=============================================================================
Adds a **per-period production-capacity constraint** to the classic fixed-setup
lot-sizing problem.  Two SmolAgents-ready tools are exported:

* ``solve_cap_lot_sizing``      → detailed *dict* (plan, inventory, setup, cost)
* ``solve_cap_lot_sizing_basic`` → simple *(production_plan, total_cost)* tuple

Required input field **`capacity`** is a list (length *T*) of the maximum
units that can be produced in each period.

Example CLI  ─────────────────────────────────────────────────────────────

```bash
echo '{"demand":[100,150,80,130],"capacity":[300,300,300,300],"setup_cost":1000,"unit_cost":50,"holding_cost":2}' | \
  python tools/cap_lot_sizing_tool.py
```

Prerequisites: same as for *lot_sizing_tool.py* (Gurobi licence, gurobipy).
"""
from __future__ import annotations
from typing import List, Dict, Tuple
import json, sys, gurobipy as gp  # type: ignore
from gurobipy import GRB  # type: ignore
from smolagents import tool

# ────────────────────────────────────────────────────────────────────────────
# Internal MILP solver
# ────────────────────────────────────────────────────────────────────────────


def _solve_cap_core(
    demand: List[float],
    capacity: List[float],
    setup_cost: float,
    unit_cost: float,
    holding_cost: float,
    initial_inventory: float,
) -> Tuple[List[float], List[float], List[int], float]:
    """Solve the capacitated lot-sizing MILP and return raw vectors & cost."""
    if len(demand) != len(capacity):
        raise ValueError("'demand' and 'capacity' must have the same length")

    T = len(demand)
    m = gp.Model("cap_lot_sizing")
    m.Params.OutputFlag = 0

    prod = m.addVars(T, lb=0.0, name="prod")
    inv = m.addVars(T, lb=0.0, name="inv")
    y = m.addVars(T, vtype=GRB.BINARY, name="setup")

    bigM = max(capacity)  # capacity already provides a natural big-M

    for t in range(T):
        prev_inv = initial_inventory if t == 0 else inv[t - 1]
        m.addConstr(prev_inv + prod[t] - demand[t] == inv[t], name=f"bal_{t}")
        m.addConstr(prod[t] <= capacity[t], name=f"cap_{t}")
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
# SmolAgents tools
# ────────────────────────────────────────────────────────────────────────────


@tool
def solve_cap_lot_sizing(
    demand: List[float],
    capacity: List[float],
    setup_cost: float,
    unit_cost: float,
    holding_cost: float,
    initial_inventory: float = 0.0,
) -> Dict[str, List[float] | float]:
    """Solve capacitated lot-sizing and return a detailed **dict**.

    Args:
        demand: Demand per period.
        capacity: Maximum producible units per period (same length as demand).
        setup_cost: Fixed cost per production run.
        unit_cost: Variable cost per produced unit.
        holding_cost: Inventory cost per unit per period.
        initial_inventory: Stock before period 1.

    Returns:
        dict with keys ``production_plan``, ``inventory``, ``setup`` and
        ``total_cost``.
    """
    plan, inv, setups, cost = _solve_cap_core(
        demand, capacity, setup_cost, unit_cost, holding_cost, initial_inventory
    )
    return {
        "production_plan": plan,
        "inventory": inv,
        "setup": setups,
        "total_cost": cost,
    }


@tool
def solve_cap_lot_sizing_basic(
    demand: List[float],
    capacity: List[float],
    setup_cost: float,
    unit_cost: float,
    holding_cost: float,
    initial_inventory: float = 0.0,
) -> Tuple[List[float], float]:
    """Solve capacitated lot sizing and return **(production_plan, total_cost)**.

    Args:
        demand (List[float]): Demand quantity for each period.
        capacity (List[float]): Maximum producible units per period.
        setup_cost (float): Fixed cost incurred when production occurs.
        unit_cost (float): Variable production cost per unit.
        holding_cost (float): Inventory carrying cost per unit per period.
        initial_inventory (float, optional): Stock before period 1. Defaults to 0.0.

    Returns:
        Tuple[List[float], float]:
            • production_plan – optimal quantity produced each period
            • total_cost – minimal total cost of production + holding + setups
    """
    plan, _inv, _setup, cost = _solve_cap_core(
        demand, capacity, setup_cost, unit_cost, holding_cost, initial_inventory
    )
    return plan, cost


# ────────────────────────────────────────────────────────────────────────────
# CLI helper
# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    params = json.load(sys.stdin)
    result = solve_cap_lot_sizing(**params)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
