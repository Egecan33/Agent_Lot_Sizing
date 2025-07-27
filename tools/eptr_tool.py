#!/usr/bin/env python3
"""
eptr2_mcp_tool.py — thin SmolAgents wrapper around eptr2.call("mcp", ...)
=======================================================================

* **fetch_mcp** → forwards arguments to `eptr.call("mcp", ...)` and returns its result (dict or DataFrame).

This tool fetches Market Clearing Price (MCP) data from the EPIAS transparency platform.
PTF (Piyasa Takas Fiyatı) is the Turkish alias for MCP, so queries about PTF will also trigger this tool.
Examples: "what is ptf today", "what is mcp yesterday", "dünkü ptf nedir", "bugünkü mcp kaç".

The agent should compute appropriate start_date and end_date based on the query (e.g., for "today", use current date as both start and end).
Dates must be in YYYY-MM-DD format. For hourly data, the result includes prices per hour.

Requires EPIAS credentials (direct login; no file needed).

Example shell run
-----------------
```bash
echo '{"start_date":"2025-07-23","end_date":"2025-07-23"}' \
  | python tools/eptr2_mcp_tool.py
"""
from __future__ import annotations
import json, sys
from typing import Any, Union
from smolagents import tool
import eptr2  # make sure `pip install eptr2[allextras]`


@tool
def fetch_mcp(start_date: str, end_date: str) -> Union[dict, Any]:
    """Fetch Market Clearing Price (MCP) data using eptr2.

    This tool can also be triggered for PTF queries, as PTF is an alias for MCP.
    Examples of queries that trigger this: "what is ptf today", "what is mcp yesterday", "dünkü ptf nedir", "bugünkü mcp kaç".

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format (inclusive).

    Returns:
        dict or DataFrame: MCP data with dates, hours, and prices (in TRY/MWh).
        If pandas is installed, returns a DataFrame for tabular data; otherwise, a dict/list.
    """
    from eptr2 import EPTR2

    eptr = EPTR2(
        username="aktanegecan@gmail.com", password="!Yonca33"
    )  # Replace with actual EPIAS credentials
    return eptr.call("mcp", start_date=start_date, end_date=end_date)


# convenient CLI passthrough
if __name__ == "__main__":
    params = json.load(sys.stdin)
    out = fetch_mcp(**params)
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
