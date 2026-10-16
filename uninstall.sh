#!/usr/bin/env bash

BLUE='\033[38;5;39m'
YELLOW='\033[38;5;220m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
WHITE='\033[1;97m'
BOLD='\033[1m'
DIM='\033[2m'
GRAY='\033[90m'
RESET='\033[0m'

echo -e "\n${BLUE}─────────────────────────────────────────────────────────────${RESET}"
echo -e "  ${WHITE}S H P A K${RESET}  ${GRAY}│${RESET}  ${CYAN}uninstaller${RESET}  ${GRAY}·  developer ai translation suite${RESET}"
echo -e "${YELLOW}─────────────────────────────────────────────────────────────${RESET}"

# 1. Remove LaunchAgent service if left behind
PLIST="${HOME}/Library/LaunchAgents/com.llm-translate.proxy.plist"
if [ -f "${PLIST}" ]; then
    launchctl unload "${PLIST}" 2>/dev/null || true
    rm -f "${PLIST}"
fi

# 2. Remove legacy plugins if left behind
rm -rf "${HOME}/.gemini/config/plugins/llm-translate" 2>/dev/null || true
rm -rf "${HOME}/.gemini/config/plugins/translate-to-ua" 2>/dev/null || true
rm -f "${HOME}/.claude/commands/tr.md" "${HOME}/.claude/commands/tr-last.md" 2>/dev/null || true

# 3. Remove all Shpak and legacy symlinks from ~/.local/bin
BIN_DIR="${HOME}/.local/bin"
rm -f "${BIN_DIR}/spk" "${BIN_DIR}/shpak"
rm -f "${BIN_DIR}/agy-spk" "${BIN_DIR}/agy-shpak"
rm -f "${BIN_DIR}/claude-spk" "${BIN_DIR}/claude-shpak"
rm -f "${BIN_DIR}/codex-spk" "${BIN_DIR}/codex-shpak"
rm -f "${BIN_DIR}/cursor-spk" "${BIN_DIR}/cursor-shpak"

# Legacy
rm -f "${BIN_DIR}/tr" "${BIN_DIR}/ag-tr" "${BIN_DIR}/claude-tr" "${BIN_DIR}/codex-tr" "${BIN_DIR}/cursor-tr" "${BIN_DIR}/llm-tr"

echo -e "   ${GREEN}✔ Removed symlinks from ~/.local/bin${RESET}"
echo -e "   ${GREEN}✔ Cleaned up configs and cache${RESET}"
echo ""
echo -e "${GREEN}🎉 Uninstallation complete!${RESET}"
