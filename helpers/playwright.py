"""Playwright binary discovery helper for the browser plugin.

Recreates the ensure_playwright_binary() function that was originally
in python/helpers/playwright.py (removed from A0 core in commit 4a75a9b).
"""
import glob
import os
import subprocess


def ensure_playwright_binary() -> str:
    """Locate the Playwright Chromium headless shell binary.

    Search order:
      1. /a0/tmp/playwright/ — Agent Zero's own downloaded playwright browsers
      2. ~/.cache/ms-playwright/ — standard Playwright download cache
      3. patchright Python API — asks patchright where its chromium lives
      4. playwright Python API — asks playwright where its chromium lives

    Returns:
        Absolute path to the Chromium executable.

    Raises:
        FileNotFoundError: if no Chromium binary can be located.
    """
    # Search patterns ordered by preference (headless_shell first, then chrome)
    search_roots = [
        "/a0/tmp/playwright",
        os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright"),
    ]

    binary_names = [
        "headless_shell",
        "chrome",
        "chrome.exe",
    ]

    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for name in binary_names:
            pattern = os.path.join(root, "**", name)
            matches = sorted(glob.glob(pattern, recursive=True), reverse=True)
            for match in matches:
                if os.path.isfile(match):
                    return match

    # Fallback: ask patchright (standalone Playwright API)
    try:
        from patchright.sync_api import sync_playwright  # type: ignore
        p = sync_playwright().start()
        path = p.chromium.executable_path
        p.stop()
        if path and os.path.isfile(path):
            return path
    except Exception:
        pass

    # Fallback: ask playwright
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        p = sync_playwright().start()
        path = p.chromium.executable_path
        p.stop()
        if path and os.path.isfile(path):
            return path
    except Exception:
        pass

    raise FileNotFoundError(
        "Playwright Chromium binary not found. "
        "Run: playwright install chromium  (or patchright install chromium)"
    )
