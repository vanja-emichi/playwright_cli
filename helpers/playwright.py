"""Playwright binary discovery helper for the browser plugin.

Locates an existing Chromium executable from known cache locations.
Used by PlaywrightCliBackend to determine PLAYWRIGHT_BROWSERS_PATH.

Search order:
  1. /a0/tmp/playwright/ — Agent Zero downloaded Playwright browsers
  2. ~/.cache/ms-playwright/ — standard Playwright download cache

If neither is found, raises FileNotFoundError.
Run: playwright-cli install  (or use the plugin Initialize button)
"""
import glob
import os


def ensure_playwright_binary() -> str:
    """Locate the Playwright Chromium executable.

    Returns:
        Absolute path to the Chromium executable.

    Raises:
        FileNotFoundError: if no Chromium binary can be located.
    """
    search_roots = [
        "/a0/tmp/playwright",
        os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright"),
    ]

    binary_names = ["headless_shell", "chrome", "chrome.exe"]

    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for name in binary_names:
            pattern = os.path.join(root, "**", name)
            matches = sorted(glob.glob(pattern, recursive=True), reverse=True)
            for match in matches:
                if os.path.isfile(match):
                    return match

    raise FileNotFoundError(
        "Playwright Chromium binary not found. "
        "Run: playwright-cli install  (or use the plugin Initialize button)"
    )
