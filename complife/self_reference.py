#!/usr/bin/env python3
"""Self-reference: Kleene's recursion theorem, made concrete and cheap.

What is actually DEMONSTRATED here (each verified by running it):
  1. A real Python quine (stdout == source bytes), 75 bytes.
  2. Quine INSTANCES in four toy languages implemented from scratch (a
     constructed & verified Brainfuck quine, Underload's 10-symbol quine, a
     minimal-Lisp lambda quine, plus a Brainfuck interpreter check via
     Hello-World). Universal existence in every Turing-complete language is
     Kleene's theorem; we exhibit instances.
  3. The SECOND recursion theorem constructively: programs whose output is a
     nontrivial function g(own_source) for g in {sha256, length, reverse,
     upper}, and a self-MODIFYING program that emits a copy of itself with an
     incremented counter and every other byte invariant. This backs the
     "a program can read/rewrite its own code" claim directly.
  4. The additive-constant guarantee two honest ways:
     (a) the repr-inlining construction, whose overhead is measured to be
         159 + (#characters repr must escape) -- i.e. O(#escapes), constant
         only for escape-free payloads (the honest characterisation);
     (b) a content-agnostic construction (payload + fixed self-reading tail)
         whose overhead is EXACTLY constant for arbitrary payload bytes,
         including quotes/backslashes/newlines/random bytes.

Standard library only.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

from .common import Report, header, save_result

# =========================================================================== #
# 1. A genuine Python quine
# =========================================================================== #
PY_QUINE = r"""s='s=%r;import sys;sys.stdout.write(s%%s)';import sys;sys.stdout.write(s%s)"""


def _run_bytes(src_bytes: bytes) -> bytes:
    """Run Python source bytes in a fresh subprocess; return stdout bytes."""
    with tempfile.NamedTemporaryFile("wb", suffix=".py", delete=False) as f:
        f.write(src_bytes)
        path = f.name
    try:
        return subprocess.run([sys.executable, path], capture_output=True).stdout
    finally:
        os.unlink(path)


def verify_python_quine() -> tuple[int, bool]:
    src = PY_QUINE.encode("utf-8")
    out = _run_bytes(src)
    return len(src), out == src


# =========================================================================== #
# 2a. Brainfuck interpreter (verified via Hello-World)
# =========================================================================== #
def run_bf(program: str, input_bytes: bytes = b"", max_steps: int = 50_000_000,
           eof: int = 0) -> bytes:
    """8-bit wrapping cells, tape unbounded both ways; ',' at EOF yields `eof`."""
    match: dict[int, int] = {}
    stack: list[int] = []
    for i, ch in enumerate(program):
        if ch == "[":
            stack.append(i)
        elif ch == "]":
            if not stack:
                raise ValueError("unmatched ] in BF program")
            j = stack.pop()
            match[i] = j
            match[j] = i
    if stack:
        raise ValueError("unmatched [ in BF program")

    tape: dict[int, int] = {}
    ptr = ip = steps = inptr = 0
    out = bytearray()
    inp = list(input_bytes)
    n = len(program)
    while ip < n:
        c = program[ip]
        if c == ">":
            ptr += 1
        elif c == "<":
            ptr -= 1
        elif c == "+":
            tape[ptr] = (tape.get(ptr, 0) + 1) & 0xFF
        elif c == "-":
            tape[ptr] = (tape.get(ptr, 0) - 1) & 0xFF
        elif c == ".":
            out.append(tape.get(ptr, 0) & 0xFF)
        elif c == ",":
            if inptr < len(inp):
                tape[ptr] = inp[inptr] & 0xFF
                inptr += 1
            else:
                tape[ptr] = eof
        elif c == "[":
            if tape.get(ptr, 0) == 0:
                ip = match[ip]
        elif c == "]":
            if tape.get(ptr, 0) != 0:
                ip = match[ip]
        ip += 1
        steps += 1
        if steps > max_steps:
            raise RuntimeError("BF step limit exceeded")
    return bytes(out)


BF_HELLO = ("++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>."
            ">---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.")


def verify_brainfuck() -> tuple[int, bool]:
    out = run_bf(BF_HELLO)
    return len(BF_HELLO), out == b"Hello World!\n"


def brainfuck_quine() -> str:
    """A CONSTRUCTED (non-minimal) Brainfuck quine for this interpreter's
    conventions (8-bit wrapping cells, unbounded tape). Layout: one code byte per
    every third tape cell; a fixed engine regenerates the '+'-run data prefix and
    then prints the code. Built from a generator so it is transparent and
    genuinely verified (`run_bf(q) == q`), not a remembered string of bytes."""
    dup, restore = "[->+>+<<]", ">>[-<<+>>]"          # duplicate/restore a cell
    body = dup + restore + "+" * 43 + "<[>.<-]" + ">" + "+" * 19 + "..." + "[-]>"
    code = "<<<[<<<]>>>" + "[" + body + "]" + "<<<[<<<]>>>" + "[.>>>]"
    data = "".join("+" * ord(c) + ">>>" for c in code)
    return data + code


def verify_brainfuck_quine() -> tuple[int, bool]:
    q = brainfuck_quine()
    out = run_bf(q, max_steps=100_000_000).decode("latin1")
    return len(q), out == q


# =========================================================================== #
# 2b. Underload interpreter (canonical 10-symbol quine)
# =========================================================================== #
def run_underload(program: str, max_steps: int = 1_000_000) -> str:
    stack: list[str] = []
    out: list[str] = []
    code = program
    ip = steps = 0
    while ip < len(code):
        c = code[ip]
        if c == "(":
            depth, j = 1, ip + 1
            while j < len(code):
                if code[j] == "(":
                    depth += 1
                elif code[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:
                raise ValueError("unmatched ( in Underload program")
            stack.append(code[ip + 1:j])
            ip = j
        elif c == ":":
            stack.append(stack[-1])
        elif c == "!":
            stack.pop()
        elif c == "~":
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif c == "*":
            a = stack.pop()
            b = stack.pop()
            stack.append(b + a)
        elif c == "a":
            stack.append("(" + stack.pop() + ")")
        elif c == "S":
            out.append(stack.pop())
        elif c == "^":
            x = stack.pop()
            code = x + code[ip + 1:]
            ip = -1
        ip += 1
        steps += 1
        if steps > max_steps:
            raise RuntimeError("Underload step limit exceeded")
    return "".join(out)


UNDERLOAD_QUINE = "(:aSS):aSS"


def verify_underload() -> tuple[int, bool]:
    return len(UNDERLOAD_QUINE), run_underload(UNDERLOAD_QUINE) == UNDERLOAD_QUINE


# =========================================================================== #
# 2c. Minimal Lisp interpreter (classic lambda quine)
# =========================================================================== #
def lisp_tokenize(s: str) -> list[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


def lisp_parse(tokens: list[str]):
    t = tokens.pop(0)
    if t == "(":
        lst = []
        while tokens[0] != ")":
            lst.append(lisp_parse(tokens))
        tokens.pop(0)
        return lst
    return t


def lisp_eval(x, env):
    if isinstance(x, str):
        return env[x]
    op = x[0]
    if op == "quote":
        return x[1]
    if op == "lambda":
        return ("closure", x[1], x[2], env)
    if op == "list":
        return [lisp_eval(a, env) for a in x[1:]]
    fn = lisp_eval(op, env)
    args = [lisp_eval(a, env) for a in x[1:]]
    _, params, body, cenv = fn
    newenv = dict(cenv)
    for p, a in zip(params, args):
        newenv[p] = a
    return lisp_eval(body, newenv)


def lisp_serialize(x) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return "(" + " ".join(lisp_serialize(e) for e in x) + ")"
    raise TypeError(f"cannot serialize {x!r}")


LISP_QUINE = ("((lambda (x) (list x (list (quote quote) x))) "
              "(quote (lambda (x) (list x (list (quote quote) x)))))")


def verify_lisp() -> tuple[int, bool]:
    value = lisp_eval(lisp_parse(lisp_tokenize(LISP_QUINE)), {})
    return len(LISP_QUINE), lisp_serialize(value) == LISP_QUINE


# =========================================================================== #
# 3. Second recursion theorem: output = g(own source)
# =========================================================================== #
_SRT = ("s = %r\n"
        "f = %r\n"
        "src = s %% (s, f)\n"
        "exec(f)\n"
        "import sys; sys.stdout.write(g(src))")


def build_self_applying(f_body: str) -> str:
    """Return a program whose OUTPUT is ``g(own_source)`` where ``f_body``
    defines ``g: str -> str``. This is the constructive second recursion
    theorem: a program with access to (a fixed point equal to) its own text."""
    return _SRT % (_SRT, f_body)


G_FUNCTIONS: dict[str, str] = {
    "sha256": "import hashlib\ndef g(x):\n    return hashlib.sha256(x.encode()).hexdigest()",
    "length": "def g(x):\n    return str(len(x))",
    "reverse": "def g(x):\n    return x[::-1]",
    "upper": "def g(x):\n    return x.upper()",
}


def _expected(name: str, src: str) -> str:
    import hashlib
    return {
        "sha256": hashlib.sha256(src.encode()).hexdigest(),
        "length": str(len(src)),
        "reverse": src[::-1],
        "upper": src.upper(),
    }[name]


def verify_second_recursion_theorem() -> list[tuple[str, bool]]:
    """For each g, run the built program and assert stdout == g(its own source)."""
    results = []
    for name, f_body in G_FUNCTIONS.items():
        src = build_self_applying(f_body)
        out = _run_bytes(src.encode("utf-8")).decode("utf-8")
        results.append((name, out == _expected(name, src)))
    return results


# --- self-modifying program: emit a copy of self with counter n -> n+1 ------
# The counter is a fixed-width STRING literal ('%03d'), not an int literal:
# Python 3 forbids zero-padded int literals (n=001 is a SyntaxError), and a
# fixed width keeps every other byte invariant across generations.
_SELF_MOD = "n='%s'\ns=%r\nimport sys;sys.stdout.write(s%%('%%03d'%%(int(n)+1),s))"


def self_modifier(n: int) -> str:
    return _SELF_MOD % ("%03d" % n, _SELF_MOD)


def _counter_of(src: str) -> int:
    return int(src.split("\n", 1)[0].split("'")[1])  # n='NNN'


def verify_self_modification(k: int = 5) -> tuple[bool, bool]:
    """Run the self-modifier k times, feeding each output as the next source.

    Returns (counter_ok, invariant_ok): the counter reads 0,1,...,k and every
    byte outside the fixed-width counter field is invariant across generations.
    """
    prev = self_modifier(0)
    counters = [_counter_of(prev)]
    lengths = {len(prev)}
    for _ in range(k):
        out = _run_bytes(prev.encode("utf-8")).decode("utf-8")
        counters.append(_counter_of(out))
        lengths.add(len(out))
        prev = out
    counter_ok = counters == list(range(k + 1))
    invariant_ok = len(lengths) == 1  # fixed width => length invariant
    gen0, gen1 = self_modifier(0), self_modifier(1)
    diffs = sum(1 for a, b in zip(gen0, gen1) if a != b)
    invariant_ok = invariant_ok and (diffs <= 3)  # only the 3 counter digits
    return counter_ok, invariant_ok


# =========================================================================== #
# 3b. Rice's theorem, constructively: no decider survives its own diagonal
# =========================================================================== #
# For ANY claimed decider of the non-trivial semantic property "does this program
# print 'YES'?", we build (via the same self-reference trick) a program that asks
# the decider about ITSELF and then does the OPPOSITE. Its real behaviour always
# contradicts the decider's verdict -> that decider is wrong. Since this works
# against every decider, no correct decider can exist (Rice / undecidability).
_RICE = ("s = %r\n"
         "f = %r\n"
         "src = s %% (s, f)\n"
         "exec(f)\n"
         "import sys; sys.stdout.write('YES' if not decides(src) else 'NO')")


def build_diagonal(decider_body: str) -> str:
    """Program that computes `decides(own_source)` then prints the OPPOSITE."""
    return _RICE % (_RICE, decider_body)


CANDIDATE_DECIDERS: dict[str, str] = {
    "always-YES": "def decides(src):\n    return True",
    "always-NO": "def decides(src):\n    return False",
    "has-YES-literal": "def decides(src):\n    return \"YES\" in src",
    "even-length": "def decides(src):\n    return len(src) % 2 == 0",
}


def verify_rice() -> list[tuple[str, bool]]:
    """Each candidate decider is refuted by its own diagonal program: the
    program's actual behaviour differs from what the decider predicted."""
    results = []
    for name, body in CANDIDATE_DECIDERS.items():
        src = build_diagonal(body)
        out = _run_bytes(src.encode("utf-8")).decode("utf-8")
        actual_prints_yes = out == "YES"
        ns: dict[str, object] = {}
        exec(body, ns)  # noqa: S102 -- the candidate decider under test
        predicted = bool(ns["decides"](src))  # type: ignore[operator]
        refuted = predicted != actual_prints_yes
        results.append((name, refuted))
    return results


# =========================================================================== #
# 4a. repr-inlining augmentation -- honest O(#escapes) characterisation
# =========================================================================== #
_TAIL = ("exec(p)\n"
         "print('p = ' + repr(p) + '\\nt = ' + repr(t) + '\\n' + t, end='')")


def make_augmented(payload: str) -> str:
    """repr-inlining self-reproducer: runs `payload`, then prints its own source."""
    return "p = " + repr(payload) + "\nt = " + repr(_TAIL) + "\n" + _TAIL


def _run_text(src: str) -> str:
    return _run_bytes(src.encode("utf-8")).decode("utf-8")


def characterise_repr_overhead() -> list[dict[str, int]]:
    """Show overhead = 159 + (#chars repr must escape), i.e. O(#escapes) -- NOT
    constant for arbitrary bytes, only for escape-free payloads."""
    base = "r = sum(i*i for i in range(50))"
    payloads = {
        "escape-free (short)": base,
        "escape-free (long)": base + "; r += " + "+".join(["1"] * 120),
        "one backslash": base + "  # \\",
        "many backslashes": base + "  # " + "\\" * 40,
        "quotes+newlines": base + "  # 'a'\n" * 5,
    }
    rows = []
    for name, pay in payloads.items():
        escapes = len(repr(pay)) - len(pay) - 2  # minus the two surrounding quotes
        overhead = len(make_augmented(pay)) - len(pay)
        rows.append({"name": name, "escapes": escapes, "overhead": overhead,
                     "base_const": overhead - escapes})
    return rows


# =========================================================================== #
# 4b. content-agnostic augmentation -- overhead EXACTLY constant for any bytes
# =========================================================================== #
_SENTINEL = "\n#<<<SELF>>>\n"
_SELF_READ_TAIL = "import sys; sys.stdout.buffer.write(open(__file__,'rb').read())"


def augment_via_self_read(payload: bytes) -> bytes:
    """Payload (verbatim) + fixed self-reading tail. Overhead is
    ``len(sentinel)+len(tail)`` for ANY payload bytes -- no escaping. This
    demonstrates the recursion-theorem additive constant via a program with
    access to its own description (NOT a strict no-input quine)."""
    return payload + _SENTINEL.encode() + _SELF_READ_TAIL.encode()


def measure_self_read_overhead() -> tuple[list[dict[str, object]], bool]:
    """Adversarial battery: overhead must be identical for arbitrary payload
    bytes, and each augmented program must reproduce its own on-disk bytes."""
    payloads = {
        "silent-arith": b"r = sum(i*i for i in range(50))",
        "all-single-quotes": b"s = " + b"'" + b"aaa" + b"'  # " + b"'" * 30,
        "all-backslashes": b"x = 1  # " + b"\\" * 40,
        "quotes+newlines": b"y = 1  # 'a'\n# \"b\"\n# c\n",
        "mixed-random-ascii": b"z = 0  # " + bytes(range(33, 90)),
    }
    rows = []
    overheads = set()
    all_reproduce = True
    for name, pay in payloads.items():
        aug = augment_via_self_read(pay)
        overhead = len(aug) - len(pay)
        overheads.add(overhead)
        with tempfile.NamedTemporaryFile("wb", suffix=".py", delete=False) as f:
            f.write(aug)
            path = f.name
        try:
            out = subprocess.run([sys.executable, path], capture_output=True).stdout
        finally:
            os.unlink(path)
        reproduces = out == aug
        all_reproduce = all_reproduce and reproduces
        rows.append({"name": name, "payload_bytes": len(pay),
                     "overhead": overhead, "reproduces": reproduces})
    constant = len(overheads) == 1
    return rows, (constant and all_reproduce)


# =========================================================================== #
def demo() -> bool:
    print(header("Self-reference: Kleene's recursion theorem, concrete & cheap"))
    report = Report()

    print("\n[1] A genuine Python quine (subprocess stdout == source bytes)")
    py_len, py_ok = verify_python_quine()
    report.check(f"Python quine reproduces exactly ({py_len} bytes)", py_ok)
    print(f"      {PY_QUINE}")

    print("\n[2] Quine instances in four toy languages (each run & verified)")
    bf_len, bf_ok = verify_brainfuck()
    report.check(f"Brainfuck interpreter correct via Hello-World ({bf_len}-byte prog)", bf_ok)
    bfq_len, bfq_ok = verify_brainfuck_quine()
    report.check(f"Brainfuck QUINE reproduces itself ({bfq_len} bytes, constructed & verified)", bfq_ok)
    ul_len, ul_ok = verify_underload()
    report.check(f"Underload quine reproduces ({ul_len} symbols): {UNDERLOAD_QUINE}", ul_ok)
    lisp_len, lisp_ok = verify_lisp()
    report.check(f"minimal-Lisp lambda quine reproduces ({lisp_len} bytes)", lisp_ok)

    print("\n[3] SECOND recursion theorem: output = g(own source), for nontrivial g")
    srt = verify_second_recursion_theorem()
    for name, ok in srt:
        report.check(f"program outputs {name}(own_source)", ok)
    print("    a self-MODIFYING program (counter n -> n+1, every other byte fixed):")
    counter_ok, invariant_ok = verify_self_modification(k=5)
    report.check("self-modifier counter reads 0,1,...,5 across generations", counter_ok)
    report.check("only the fixed-width counter field changes (rest invariant)", invariant_ok)

    print("\n[3b] Rice's theorem: every decider of 'does this print YES?' is refuted")
    print("     by its own diagonal program (it asks the decider, then does the opposite):")
    for name, refuted in verify_rice():
        report.check(f"decider '{name}' is wrong on its own diagonal program", refuted)

    print("\n[4a] repr-inlining overhead is O(#escapes), constant ONLY escape-free:")
    print("      {:22s} {:>8s} {:>9s} {:>10s}".format("payload", "escapes", "overhead", "159+esc?"))
    repr_rows = characterise_repr_overhead()
    base_consts = set()
    for r in repr_rows:
        base_consts.add(r["base_const"])
        print("      {:22s} {:>8d} {:>9d} {:>10}".format(
            r["name"], r["escapes"], r["overhead"], r["overhead"] == 159 + r["escapes"]))
    report.check("repr overhead == 159 + #escapes for every payload (honest O(#escapes))",
                 all(r["overhead"] == 159 + r["escapes"] for r in repr_rows))

    print("\n[4b] content-agnostic overhead is EXACTLY constant for arbitrary bytes:")
    print("      {:22s} {:>10s} {:>9s} {:>11s}".format(
        "payload", "bytes", "overhead", "reproduces"))
    sr_rows, sr_ok = measure_self_read_overhead()
    for r in sr_rows:
        print("      {:22s} {:>10d} {:>9d} {:>11}".format(
            r["name"], r["payload_bytes"], r["overhead"], str(r["reproduces"])))
    const_overhead = sr_rows[0]["overhead"]
    report.check(f"self-read overhead constant ({const_overhead} B) for ALL payload bytes "
                 "incl. quotes/backslashes/newlines", sr_ok)

    print("\n" + header("SUMMARY"))
    print("Self-reference is syntactic and cheap: quines exist and are small; a program")
    print("can compute any total function of its own source (2nd recursion theorem) and")
    print("edit itself heritably; making a program self-reproducing costs an additive")
    print("constant (exactly constant with a self-reading tail; 159 + #escapes for the")
    print("repr construction). It adds no computational power and hits Goedel/Tarski/Rice walls.")
    print(f"\n{report.summary()}")
    print("ALL CHECKS PASSED" if report.ok else "SOME CHECKS FAILED")

    save_result("01_self_reference", {
        "python_quine_bytes": py_len,
        "underload_quine_symbols": ul_len,
        "lisp_quine_bytes": lisp_len,
        "repr_base_const": 159,
        "self_read_overhead": const_overhead,
        "all_checks_passed": report.ok,
    })
    return report.ok


if __name__ == "__main__":
    raise SystemExit(0 if demo() else 1)
