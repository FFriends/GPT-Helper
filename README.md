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

## Mobile instructions / Мобильные инструкции

Choose the version below and copy only the text inside its code block into Custom Instructions. Both languages prohibit flattery; mobile instructions focus on communication and verification.

### Free / Go — compact, up to 1500 characters

Use the compact version for Free/Go and any Custom Instructions field limited to **1500 characters**. Spaces and line breaks are included in the length check:

- [English — up to 1500 characters](MOBILE_CUSTOM_INSTRUCTIONS_1500_EN.md)
- [Русский — до 1500 символов](MOBILE_CUSTOM_INSTRUCTIONS_1500_RU.md)

### Plus — extended instructions

Use the extended version for Plus when your Custom Instructions field accepts the full text:

- [English — extended instructions](MOBILE_CUSTOM_INSTRUCTIONS_EN.md)
- [Русский — расширенные инструкции](MOBILE_CUSTOM_INSTRUCTIONS_RU.md)

Check the limit displayed in your app before saving. If your Plus field also limits text to 1500 characters, use the compact Free/Go version. The extended version can also be used as the first message in a dedicated project or chat when it fits.

## Coop isolation rules

GPT Helper includes task-scoped rules for Coop when isolated execution is useful: assess the need,
obtain permission before VM operations or file transfers, use a separate project copy, restrict
forwarded data, check VM readiness, and review changes before returning them to the host.
Existing permission remains valid within the same task; new tasks or expanded access require new
permission. Routine file reading and editing do not require Coop without a concrete reason.

For Codex and desktop workflows, the rules are included in the
[full skill](plugins/gpt-helper/skills/verify-before-answer/SKILL.md).
Machine-specific setup belongs in local instructions.

## Coop bundled inside the skill

The `verify-before-answer` skill includes its own **explicitly invoked** installer, restricted
configuration generator, and launcher for Coop v0.6.0 on Linux x86_64, including WSL 2 hosts with
working KVM. The complete skill directory is portable without sibling plugin files:

- [English setup guide](plugins/gpt-helper/skills/verify-before-answer/coop/README.md)
- [Установка и настройка на русском](plugins/gpt-helper/skills/verify-before-answer/coop/README.ru.md)

The package verifies the official archive's pinned SHA-256, keeps its files separate from an
existing Coop installation, and supplies a PowerShell 7 wrapper for Windows/WSL. Installing the
GPT Helper plugin does **not** run this installer or create a VM. VM setup and project execution
require separate explicit commands and task-scoped permission. Live VM execution has not been
tested for this package; offline tests do not establish host compatibility.

For standalone use, copy the entire `plugins/gpt-helper/skills/verify-before-answer/` directory,
including `coop/` and `agents/`. Copying only `SKILL.md` omits the installer. The former
`plugins/gpt-helper/coop/` location has moved inside the skill; update any saved script paths.

## Structure

- `.agents/plugins/marketplace.json` — GitHub/repo marketplace
- `plugins/gpt-helper/.codex-plugin/plugin.json` — plugin manifest
- `plugins/gpt-helper/skills/verify-before-answer/SKILL.md` — full skill
- `plugins/gpt-helper/skills/verify-before-answer/coop/` — bundled Coop installer, WSL wrapper, guides, and offline tests
- `MOBILE_CUSTOM_INSTRUCTIONS_1500_EN.md` — English personalization text within 1500 characters
- `MOBILE_CUSTOM_INSTRUCTIONS_1500_RU.md` — Russian personalization text within 1500 characters
- `MOBILE_CUSTOM_INSTRUCTIONS_EN.md` — extended English instructions
- `MOBILE_CUSTOM_INSTRUCTIONS_RU.md` — extended Russian instructions

## License

MIT
