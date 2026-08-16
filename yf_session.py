"""
HTTP session helper for every yfinance call in StockLens.

Three problems this solves:

1. Yahoo Finance blocks yfinance's default session on many cloud/datacenter
   IPs (Render, AWS, etc.) even though it works fine from a home connection.
   Impersonating a real browser's TLS/HTTP fingerprint via curl_cffi is
   yfinance's own documented workaround.

2. curl_cffi's Cookies class iterates to plain cookie *name* strings
   (`for cookie in cookies` yields "B", not a Cookie object), but yfinance's
   internal retry/consent-cookie logic does `list(response.cookies)[0]` and
   expects a real cookie object with .name/.value attributes (that's what
   Python's http.cookiejar.Cookie - and `requests` - gives it). Without this
   patch, any time Yahoo returns a non-200 response and yfinance tries its
   cookie-refresh retry, it crashes with:
     AttributeError: 'str' object has no attribute 'name'
   This patches Cookies.__iter__ (once, process-wide) to yield the real
   cookie objects from the underlying jar instead, matching what yfinance
   expects.

3. Reusing ONE curl_cffi Session object for the entire lifetime of a
   long-running server (many requests over hours/days) can corrupt its
   internal C-level connection state and crash the whole process with
   SIGSEGV - this actually happened in production. get_session() therefore
   returns a brand-new, short-lived Session on every call instead of one
   shared long-lived session. This costs a little extra per-call overhead
   but avoids the crash; per-ticker results are still cached at the
   application layer (see each *_api.py module's own cache), and yfinance's
   own cookie/crumb values are cached process-wide regardless of which
   Session object is currently being used, so this doesn't mean re-fetching
   Yahoo's consent cookie on every single call.
"""

from curl_cffi.requests.cookies import Cookies

if not getattr(Cookies, "_stocklens_patched", False):
    def _iter_real_cookies(self):
        return iter(self.jar)

    Cookies.__iter__ = _iter_real_cookies
    Cookies._stocklens_patched = True

from curl_cffi import requests as curl_requests


def get_session():
    """Return a fresh curl_cffi session for a single yfinance call.
    Deliberately NOT cached/reused across calls - see module docstring point 3."""
    return curl_requests.Session(impersonate="chrome")
