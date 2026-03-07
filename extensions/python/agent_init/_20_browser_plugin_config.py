"""Browser plugin config extension — injects plugin-owned settings into AgentConfig.

Runs at slot _20_ (after _15_load_profile_settings, before _90_langfuse).
Reads browser_http_headers and browser_model_extra_params from plugin config
and injects them into agent.config so the Playwright CLI backend and tool
can read them without touching core settings.py.

Naming map (intentional difference):
  plugin config key           → AgentConfig target
  browser_http_headers        → agent.config.browser_http_headers
  browser_model_extra_params  → agent.config.browser_model.kwargs
  (old core key removed: browser_model_kwargs)
"""
import logging
from helpers.extension import Extension
from helpers import plugins

log = logging.getLogger(__name__)

_PLUGIN_NAME = "a0_playwright_cli"


class BrowserPluginConfig(Extension):
    def execute(self, **kwargs) -> None:
        cfg = plugins.get_plugin_config(_PLUGIN_NAME, self.agent)
        if not cfg:
            log.warning(
                "BrowserPluginConfig: plugin config not found for '%s' — skipping injection",
                _PLUGIN_NAME,
            )
            return

        # One-time migration: copy old core settings values to plugin config
        # Runs only when config.json does not yet exist (migrated=false from default_config.yaml)
        if not cfg.get("migrated", True):
            cfg = self._migrate_from_core_settings(cfg)

        # Inject browser_http_headers into AgentConfig
        # plugin config key: browser_http_headers → AgentConfig.browser_http_headers
        headers = cfg.get("browser_http_headers", {})
        if isinstance(headers, dict):
            self.agent.config.browser_http_headers = headers

        # Inject browser_model extra params into ModelConfig.kwargs
        # plugin config key: browser_model_extra_params → AgentConfig.browser_model.kwargs
        extra_params = cfg.get("browser_model_extra_params", {})
        if isinstance(extra_params, dict) and extra_params:
            self.agent.config.browser_model.kwargs = extra_params

    def _migrate_from_core_settings(self, current_cfg: dict) -> dict:
        """One-time migration: copy browser_http_headers + browser_model_kwargs
        from old core settings.json to plugin config.json.
        Only runs when config.json does not yet exist (migrated=false in default_config.yaml).
        Returns the updated config dict (with migrated=True).
        """
        import json
        import os

        # Derive usr/ root dynamically — 6x dirname from this extension file:
        # _20_...py → agent_init → python → extensions → browser → plugins → usr
        _p = os.path.abspath(__file__)
        for _ in range(6):
            _p = os.path.dirname(_p)
        settings_path = os.path.join(_p, "settings.json")
        headers: dict = {}
        kwargs: dict = {}

        if os.path.exists(settings_path):
            try:
                with open(settings_path) as f:
                    old_settings = json.load(f)
                headers = old_settings.get("browser_http_headers", {})
                # Parse env-format string ("KEY: VALUE\n...") if stored as string in old core settings
                if isinstance(headers, str) and headers.strip():
                    _parsed: dict = {}
                    for _line in headers.strip().splitlines():
                        if ":" in _line:
                            _k, _, _v = _line.partition(":")
                            _parsed[_k.strip()] = _v.strip()
                    headers = _parsed
                    log.info("BrowserPluginConfig: parsed env-format browser_http_headers string -> dict")
                elif not isinstance(headers, dict):
                    headers = {}
                kwargs = old_settings.get("browser_model_kwargs", {})
                if not isinstance(kwargs, dict):
                    kwargs = {}
                if headers or kwargs:
                    log.info(
                        "BrowserPluginConfig: migrating browser_http_headers=%s, "
                        "browser_model_kwargs=%s from core settings",
                        headers,
                        kwargs,
                    )
            except Exception as e:
                log.warning("BrowserPluginConfig: migration read failed (%s) — using empty defaults", e)
        else:
            log.debug("BrowserPluginConfig: no core settings.json found — migration skipped with empty defaults")

        return self._save_migrated_config(current_cfg, headers, kwargs)

    def _save_migrated_config(self, current_cfg: dict, headers: dict, kwargs: dict) -> dict:
        """Persist migrated config to plugin config.json (global user scope).
        Returns the new config dict.
        """
        new_cfg = dict(current_cfg)
        new_cfg["browser_http_headers"] = headers
        new_cfg["browser_model_extra_params"] = kwargs
        new_cfg["migrated"] = True
        try:
            plugins.save_plugin_config(_PLUGIN_NAME, "", "", new_cfg)
            log.info("BrowserPluginConfig: migration complete — config.json written with migrated=true")
        except Exception as e:
            log.warning("BrowserPluginConfig: failed to save migrated config (%s)", e)
        return new_cfg
