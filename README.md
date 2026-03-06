# Agent Zero — Browser Plugin

A Playwright CLI browser automation plugin for [Agent Zero](https://github.com/frdel/agent-zero), providing structured DOM automation via Microsoft Playwright CLI through a unified `browser_agent` tool.

## Features

- 🎭 **Playwright CLI backend** — structured DOM snapshots with stable element refs (`e1`, `e2`, ...)
- 🧩 **Plugin-owned settings** — browser config lives in the plugin, not Agent Zero core
- 🔧 **Auto-skill injection** — the official Playwright CLI skill is automatically injected into the agent system prompt
- 🌐 **Custom HTTP headers** — inject headers into all browser requests
- ⚙️ **Extra model params** — override browser LLM model kwargs per-agent
- 🔄 **One-time migration** — automatically migrates old core settings to plugin config
- 📱 **Mobile/device emulation** — emulate any device viewport
- 🕸️ **Network mocking** — intercept and mock requests
- 🎬 **DevTools tracing & video** — record sessions for debugging

## Installation

1. Copy the `browser` folder into your Agent Zero `usr/plugins/` directory:
   ```bash
   cp -r browser /path/to/agent-zero/usr/plugins/
   ```

2. Install the Playwright CLI and Chromium:
   ```bash
   npm install -g @playwright/cli@latest
   cd ~ && playwright-cli install
   ```

3. Restart Agent Zero — the plugin loads automatically.

## Configuration

Go to **Settings → Agent → Browser** to configure:

| Setting | Description | Default |
|---------|-------------|---------|
| HTTP Headers | JSON object of custom request headers | `{}` |
| Extra Model Params | JSON object of extra kwargs for the browser LLM | `{}` |

## How It Works

The plugin uses **Playwright CLI** (Microsoft) exclusively. The `browser_agent` tool:
1. Receives a natural-language task from the Agent Zero LLM
2. Opens a playwright-cli browser session
3. Takes YAML DOM snapshots with stable element references (`e1`, `e2`, ...)
4. Feeds snapshots back to the LLM which decides the next action
5. Executes actions (click, fill, goto, etc.) via playwright-cli commands
6. Returns the final result to the parent agent

The full [Playwright CLI skill](skills/playwright-cli/SKILL.md) is automatically injected into the agent system prompt.

## Plugin Structure

```
browser/
├── plugin.yaml                          # Plugin manifest (v2.0.0)
├── default_config.yaml                  # Default settings
├── tools/
│   └── browser_agent.py                 # Main browser_agent tool
├── helpers/
│   ├── playwright_cli_backend.py        # Playwright CLI backend
│   └── playwright.py                    # Playwright binary discovery
├── extensions/
│   └── python/
│       ├── agent_init/
│       │   └── _20_browser_plugin_config.py   # Config injection
│       └── system_prompt/
│           └── _16_playwright_cli_skill_prompt.py  # Skill auto-injection
├── prompts/
│   └── agent.system.tool.browser.md     # Tool system prompt
├── webui/
│   └── config.html                      # Settings UI
└── skills/
    └── playwright-cli/                  # Official Playwright CLI skill
        ├── SKILL.md
        └── references/
            ├── session-management.md
            ├── storage-state.md
            ├── request-mocking.md
            ├── running-code.md
            ├── test-generation.md
            ├── tracing.md
            └── video-recording.md
```

## Requirements

- Node.js with `@playwright/cli` installed globally (`npm install -g @playwright/cli@latest`)
- Chromium installed via `playwright-cli install`
- Agent Zero with plugin support

## Usage

The `browser_agent` tool is available to all agents when the plugin is enabled:

```json
{
  "tool_name": "browser_agent",
  "tool_args": {
    "message": "Go to https://example.com and return the page title",
    "reset": "true"
  }
}
```

Set `reset: true` to start a fresh browser session, `reset: false` to continue an existing one.
