"""Playwright CLI skill auto-injection extension.

Runs at slot _16_ (system prompt build phase).
Injects the playwright-cli SKILL.md content into the agent system prompt so the
agent can use playwright-cli commands directly via code_execution_tool (terminal).

The agent should use playwright-cli commands directly in the terminal for all
browser/web tasks — NOT the browser_agent tool.
"""
import logging
import os
from helpers.extension import Extension
from agent import LoopData

log = logging.getLogger(__name__)


class PlaywrightCliSkillPrompt(Extension):

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs,
    ):
        # Derive SKILL.md path relative to this extension file:
        # _16_...py → system_prompt → python → extensions → <plugin_root>
        _p = os.path.abspath(__file__)
        for _ in range(4):
            _p = os.path.dirname(_p)
        skill_md_path = os.path.join(_p, "skills", "playwright-cli", "SKILL.md")

        if not os.path.isfile(skill_md_path):
            log.warning(
                "PlaywrightCliSkillPrompt: SKILL.md not found at '%s' — skipping injection",
                skill_md_path,
            )
            return

        try:
            skill_content = open(skill_md_path, encoding="utf-8").read()
        except Exception as e:
            log.warning("PlaywrightCliSkillPrompt: failed to read SKILL.md (%s)", e)
            return

        system_prompt.append(
            "\n\n# Browser Automation — Important Instructions\n"
            "The **playwright_cli** skill is active for all browser and web tasks.\n"
            "- **ALWAYS** use `playwright-cli` commands directly via `code_execution_tool` (terminal runtime) for any web browsing, navigation, or data extraction tasks.\n"
            "- Use a named session with `-s=<name>` to keep state between commands.\n"
            "- Always `close` the session when done.\n"
            "- **DO NOT** use the `browser_agent` tool — use `playwright-cli` terminal commands directly instead.\n\n"
            "# Browser Automation Skill (playwright-cli)\n"
            + skill_content
        )
        log.debug("PlaywrightCliSkillPrompt: playwright-cli SKILL.md injected into system prompt")
