# frontend/cookies.py
"""
Robust cookie manager helper.

Attempts to use streamlit_cookies_manager.EncryptedCookieManager but falls back to
a simple in-memory shim when that is unavailable or failing. This avoids a
blank Streamlit screen due to blocking waits or duplicate-component errors.
"""
import os
import logging

logging.basicConfig(level=logging.INFO)

try:
    from streamlit_cookies_manager import EncryptedCookieManager
    COOKIE_PASSWORD = os.environ.get("MENTESA_COOKIE_PASSWORD", "super_secret_key")
    # Create a single instance; do NOT pass `key=` (older versions don't accept it)
    _cookies = EncryptedCookieManager(prefix="mentesa_", password=COOKIE_PASSWORD)
    _is_shim = False
except Exception as e:
    logging.warning("EncryptedCookieManager unavailable or failed to initialize: %s", e)
    _cookies = None
    _is_shim = True

class _ShimCookies(dict):
    def ready(self):
        return True
    def save(self):
        # shim has no persistence
        return
    def delete(self, k):
        try:
            dict.pop(self, k)
        except KeyError:
            pass
    def get(self, k, default=None):
        return dict.get(self, k, default)
    def __setitem__(self, k, v):
        return dict.__setitem__(self, k, v)

_shim_instance = _ShimCookies()

def ensure_ready():
    """
    Return the cookie manager object. This function will NOT call st.stop() so
    it won't block the UI. The returned object always has:
      - ready() -> bool
      - save()
      - delete(key)
      - get(key)
      - __setitem__(key, val)
    If the EncryptedCookieManager couldn't be created, a shim is returned.
    """
    if _cookies is not None:
        return _cookies
    return _shim_instance
