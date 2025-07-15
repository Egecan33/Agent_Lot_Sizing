# Agent Lot Sizing

This repository provides a deterministic lot-sizing solver tool using Gurobi, wrapped for agent orchestration.

## Structure

- `agent.py`: Main agent orchestration script.
- `tools/lot_sizing_tool.py`: Lot-sizing solver tool (deterministic, single-item, uncapacitated/capacitated, with fixed setup costs).
- `tools/__init__.py`: Package initializer.
- `requirements.txt`: Python dependencies.
- `examples/sample_query.txt`: Example query input for the solver.
- `README.md`: Documentation and usage instructions.

## Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Requires Python >=3.9 and Gurobi (gurobipy >=10.0).

2. **Run the solver tool**:
   ```bash
   python tools/lot_sizing_tool.py < examples/sample_query.txt
   ```
   Or use via agent orchestration in `agent.py`.

## Example Query
See `examples/sample_query.txt` for input format.

## License
Proprietary or specify your license here.
