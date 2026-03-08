"""Playwright CLI skill auto-injection extension.

Runs at slot _16_ (system prompt build phase).
Injects the playwright-cli SKILL.md content into the agent system prompt so the
agent understands what browser capabilities are available through the browser_agent tool.

The browser_agent tool uses PlaywrightCliBackend internally — the skill content here
serves as reference documentation only. The agent should always use the browser_agent
tool for browser tasks, NOT run playwright-cli commands directly in the terminal.
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
            "\n\n# Browser Automation Skill Reference (playwright-cli)\n"
            "The `browser_agent` tool uses **playwright-cli** as its browser backend.\n"
            "The following skill reference describes available browser commands and capabilities.\n"
            "Always use the `browser_agent` tool for web browsing — do not run playwright-cli commands directly in the terminal.\n\n"
            + skill_content
        )
        log.debug("PlaywrightCliSkillPrompt: playwright-cli SKILL.md injected into system prompt")
