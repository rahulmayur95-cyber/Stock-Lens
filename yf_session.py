"""
Shared HTTP session for every yfinance call in StockLens.

Two problems this solves:

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

All modules that call yfinance should import get_session() from here rather
than building their own curl_cffi Session - this also means one shared
cookie/crumb cache across the whole app instead of each module fetching its
own, which cuts down the number of Yahoo requests per page view.
"""

from curl_cffi.requests.cookies import Cookies

if not getattr(Cookies, "_stocklens_patched", False):
    def _iter_real_cookies(self):
        return iter(self.jar)

    Cookies.__iter__ = _iter_real_cookies
    Cookies._stocklens_patched = True

from curl_cffi import requests as curl_requests

_session = curl_requests.Session(impersonate="chrome")


def get_session():
    """Return the shared curl_cffi session used for all yfinance calls."""
    return _session
