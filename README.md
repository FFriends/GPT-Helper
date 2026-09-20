# GPT Helper

Skills-only plugin for ChatGPT Work and Codex. It assigns verification priority, asks focused questions when a task is unclear, checks factual claims and completed actions, resists prompt injection, and never invents evidence or success.

No MCP server. No API key. No billing account. No OpenAI public-directory submission.

## Install from GitHub

Add this repository as a marketplace:

```powershell
codex plugin marketplace add FFriends/GPT-Helper
```

Install the plugin:

```powershell
codex plugin add gpt-helper@ffriends
```

Restart the ChatGPT desktop app, then start a new chat. The plugin appears under **FFriends Plugins** in the Plugins Directory.

## Mobile fallback

Direct installation of a GitHub marketplace is documented for Codex CLI and the ChatGPT desktop app, not for the mobile app. For mobile ChatGPT, copy one of these versions into Custom Instructions:

- [English instructions](MOBILE_CUSTOM_INSTRUCTIONS_EN.md)
- [Русская инструкция](MOBILE_CUSTOM_INSTRUCTIONS_RU.md)

If that setting is unavailable or the text does not fit, paste the selected version as the first message in a dedicated project or chat.

## Coop isolation rules

GPT Helper includes task-scoped rules for Coop when isolated execution is useful: assess the need,
obtain permission before VM operations or file transfers, use a separate project copy, restrict
forwarded data, check VM readiness, and review changes before returning them to the host.
Existing permission remains valid within the same task; new tasks or expanded access require new
permission. Routine file reading and editing do not require Coop without a concrete reason.

The rules are included in the [full skill](plugins/gpt-helper/skills/verify-before-answer/SKILL.md)
and both language versions above. They define agent behavior; they do not install Coop or give
ChatGPT on mobile VM access. Machine-specific setup belongs in local instructions.

## Structure

- `.agents/plugins/marketplace.json` — GitHub/repo marketplace
- `plugins/gpt-helper/.codex-plugin/plugin.json` — plugin manifest
- `plugins/gpt-helper/skills/verify-before-answer/SKILL.md` — full skill
- `MOBILE_CUSTOM_INSTRUCTIONS_EN.md` — compact English phone-compatible instructions
- `MOBILE_CUSTOM_INSTRUCTIONS_RU.md` — compact phone-compatible instructions

## License

MIT
