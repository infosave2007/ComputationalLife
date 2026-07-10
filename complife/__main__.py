#!/usr/bin/env python3
"""Run all four Computational Life modules end to end.

    python -m complife            # run everything
    python -m complife 01 03      # run only the named modules

Exit code is 0 iff every module's self-verification passed.
"""

from __future__ import annotations

import sys
from typing import Callable

from . import (
    induction,
    lethal_mutagenesis,
    physical_limits,
    quantum,
    replication,
    self_model,
    self_reference,
)
from .common import header

MODULES: dict[str, Callable[[], bool]] = {
    "01": self_reference.demo,
    "02": self_model.demo,
    "03": replication.demo,
    "04": physical_limits.demo,
    "05": quantum.demo,
    "06": induction.demo,
    "07": lethal_mutagenesis.demo,   # a practical application of module 03
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    keys = [a.zfill(2) for a in argv] if argv else list(MODULES)
    unknown = [k for k in keys if k not in MODULES]
    if unknown:
        print(f"unknown module(s): {unknown}; choose from {list(MODULES)}")
        return 2

    results: dict[str, bool] = {}
    for i, k in enumerate(keys):
        if i:
            print("\n\n")
        results[k] = MODULES[k]()

    print("\n\n" + header("MASTER SUMMARY"))
    for k in keys:
        print(f"   module {k}: {'PASS' if results[k] else 'FAIL'}")
    all_ok = all(results.values())
    print("\nALL MODULES PASSED" if all_ok else "SOME MODULES FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
