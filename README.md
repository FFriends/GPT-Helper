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

Direct installation of a GitHub marketplace is documented for Codex CLI and the ChatGPT desktop app, not for the mobile app. For mobile ChatGPT, copy the text from [MOBILE_CUSTOM_INSTRUCTIONS_RU.md](MOBILE_CUSTOM_INSTRUCTIONS_RU.md) into Custom Instructions. If that setting is unavailable, paste it as the first message in a dedicated project or chat.

## Structure

- `.agents/plugins/marketplace.json` — GitHub/repo marketplace
- `plugins/gpt-helper/.codex-plugin/plugin.json` — plugin manifest
- `plugins/gpt-helper/skills/verify-before-answer/SKILL.md` — full skill
- `MOBILE_CUSTOM_INSTRUCTIONS_RU.md` — compact phone-compatible instructions

## License

MIT
