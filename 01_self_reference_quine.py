#!/usr/bin/env python3
"""Runnable shim -> complife.self_reference. See that module and the README.

Kept so `python3 01_self_reference_quine.py` still works from the repo root;
the real, tested implementation lives in the importable package.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from complife.self_reference import demo  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
