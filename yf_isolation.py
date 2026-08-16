"""
Isolates risky yfinance/curl_cffi calls in a separate short-lived process.

curl_cffi (used to bypass Yahoo Finance blocking cloud IPs) has a low-level
(C-code) crash that has been observed in production on Render: SIGSEGV.
Python's try/except CANNOT catch this - it happens below the Python
interpreter entirely. Left unguarded, one crashing request kills the ENTIRE
gunicorn worker process, taking the whole site down for every user until
Render restarts it (and it can keep crash-looping on the next request).

Running the risky call in a forked child process means: if it crashes, only
that short-lived child dies. The parent (the actual web server handling
everyone's requests) just sees the child exited abnormally and treats it the
same as any other "data unavailable" failure, instead of dying too.
"""

import sys
import multiprocessing


def _get_context():
    """Use "fork" where available (Linux/Mac, including Render) since it's
    fast and lightweight. Windows doesn't support "fork" at all - fall back
    to the platform default ("spawn" on Windows) there so this still works
    for local development."""
    try:
        return multiprocessing.get_context("fork")
    except ValueError:
        return multiprocessing.get_context()


def _worker(func, args, kwargs, queue):
    try:
        result = func(*args, **kwargs)
        queue.put(("ok", result))
    except Exception as e:
        queue.put(("error", repr(e)))


def run_isolated(func, *args, timeout=20, **kwargs):
    """
    Run func(*args, **kwargs) in an isolated child process and return its
    result. Returns None if the child crashed (e.g. SIGSEGV), timed out, or
    raised an exception - never raises itself, so callers can treat None
    exactly like any other "data unavailable" case.
    func's return value must be picklable (plain dicts/lists/strings/numbers
    are fine - that's all every yfinance-wrapping function here returns).
    func itself must also be picklable by reference (a module-level function,
    not a local closure or lambda) since on platforms using "spawn" (Windows)
    the child re-imports it rather than inheriting it directly.
    """
    name = getattr(func, "__name__", str(func))
    ctx = _get_context()
    queue = ctx.Queue()
    process = ctx.Process(target=_worker, args=(func, args, kwargs, queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join(5)
        print(f"[yf_isolation] {name} timed out after {timeout}s", file=sys.stderr, flush=True)
        return None

    if process.exitcode != 0:
        print(f"[yf_isolation] {name} crashed (exit code {process.exitcode})", file=sys.stderr, flush=True)
        return None

    try:
        status, payload = queue.get(timeout=2)
    except Exception:
        print(f"[yf_isolation] {name} produced no result", file=sys.stderr, flush=True)
        return None

    if status == "error":
        print(f"[yf_isolation] {name} raised: {payload}", file=sys.stderr, flush=True)
        return None

    return payload
