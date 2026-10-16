#!/usr/bin/env bash

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║           🗑️  Uninstalling ag-tr & llm-translate CLI       ║${RESET}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${RESET}"

# 1. Remove LaunchAgent service if left behind
PLIST="${HOME}/Library/LaunchAgents/com.llm-translate.proxy.plist"
if [ -f "${PLIST}" ]; then
    launchctl unload "${PLIST}" 2>/dev/null || true
    rm -f "${PLIST}"
fi

# 2. Remove plugins if left behind
rm -rf "${HOME}/.gemini/config/plugins/llm-translate" 2>/dev/null || true
rm -rf "${HOME}/.gemini/config/plugins/translate-to-ua" 2>/dev/null || true
rm -f "${HOME}/.claude/commands/tr.md" "${HOME}/.claude/commands/tr-last.md" 2>/dev/null || true

# 3. Remove symlinks
rm -f "${HOME}/.local/bin/tr"
rm -f "${HOME}/.local/bin/ag-tr"

echo -e "   ${GREEN}✔ Removed symlinks from ~/.local/bin${RESET}"
echo -e "   ${GREEN}✔ Cleaned up plugins and configs${RESET}"
echo ""
echo -e "${GREEN}🎉 Uninstallation complete!${RESET}"
