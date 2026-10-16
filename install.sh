#!/usr/bin/env bash
set -e

# Colors
BLUE='\033[38;5;39m'
YELLOW='\033[38;5;220m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BLUE}${BOLD}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}${BOLD}║              🐦 Installing Shpak (spk) AI Suite             ║${RESET}"
echo -e "${YELLOW}${BOLD}╚════════════════════════════════════════════════════════════╝${RESET}"

BIN_DIR="${HOME}/.local/bin"
mkdir -p "${BIN_DIR}"

# Check if running from inside local cloned repo or via curl/remote
if [ -f "$(dirname "$0")/agy-shpak" ] && [ -f "$(dirname "$0")/shpak-cli" ]; then
    INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    # Remote curl execution: install to ~/.shpak
    INSTALL_DIR="${HOME}/.shpak"
    REPO_URL="https://github.com/mo0rych0k/shpak.git"

    if [ -d "${INSTALL_DIR}/.git" ]; then
        echo -e "   🔄 Updating existing Shpak installation in ${INSTALL_DIR}..."
        git -C "${INSTALL_DIR}" pull --quiet
    else
        echo -e "   📦 Cloning Shpak into ${INSTALL_DIR}..."
        rm -rf "${INSTALL_DIR}"
        git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}" --quiet
    fi
fi

# 1. Ensure permissions
chmod +x "${INSTALL_DIR}/agy-shpak"
chmod +x "${INSTALL_DIR}/shpak-cli"

# 2. Local workspace symlinks
ln -sf shpak-cli "${INSTALL_DIR}/spk" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/agy-spk" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/claude-spk" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/codex-spk" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/cursor-spk" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/claude-shpak" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/codex-shpak" 2>/dev/null || true
ln -sf agy-shpak "${INSTALL_DIR}/cursor-shpak" 2>/dev/null || true

# Clean up any obsolete legacy symlinks in installation directory
rm -f "${INSTALL_DIR}/ag-tr" "${INSTALL_DIR}/tr" "${INSTALL_DIR}/claude-tr" "${INSTALL_DIR}/codex-tr" "${INSTALL_DIR}/cursor-tr" "${INSTALL_DIR}/llm-tr" 2>/dev/null || true

# 3. Symlink to ~/.local/bin
# Primary short commands:
ln -sf "${INSTALL_DIR}/shpak-cli" "${BIN_DIR}/spk"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/agy-spk"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/claude-spk"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/codex-spk"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/cursor-spk"

# Full aliases:
ln -sf "${INSTALL_DIR}/shpak-cli" "${BIN_DIR}/shpak"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/agy-shpak"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/claude-shpak"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/codex-shpak"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/cursor-shpak"

# Clean obsolete legacy links in ~/.local/bin
rm -f "${BIN_DIR}/ag-tr" "${BIN_DIR}/tr" "${BIN_DIR}/claude-tr" "${BIN_DIR}/codex-tr" "${BIN_DIR}/cursor-tr" "${BIN_DIR}/llm-tr" 2>/dev/null || true

echo -e "   ${GREEN}✔ Symlinked spk & shpak to ${BIN_DIR}/spk${RESET}"
echo -e "   ${GREEN}✔ Symlinked agy-spk to ${BIN_DIR}/agy-spk (Antigravity)${RESET}"
echo -e "   ${GREEN}✔ Symlinked claude-spk to ${BIN_DIR}/claude-spk (Claude Code)${RESET}"
echo -e "   ${GREEN}✔ Symlinked codex-spk to ${BIN_DIR}/codex-spk (Codex CLI)${RESET}"
echo -e "   ${GREEN}✔ Symlinked cursor-spk to ${BIN_DIR}/cursor-spk (Cursor Agent)${RESET}"

# 4. Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo -e "${YELLOW}⚠️  Note: ${BIN_DIR} is not in your current PATH.${RESET}"
    echo -e "   Add this line to your ${CYAN}~/.zshrc${RESET} or ${CYAN}~/.bashrc${RESET}:"
    echo -e "   ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
fi

echo ""
echo -e "${GREEN}🎉 Shpak (spk) installed successfully!${RESET}"
echo -e "${BLUE}────────────────────────────────────────────────────────────${RESET}"
echo -e "1. Quick AI CLI wrappers with transparent translation:"
echo -e "   • ${CYAN}agy-spk${RESET} (or ${CYAN}agy-shpak${RESET})     - Antigravity CLI"
echo -e "   • ${CYAN}claude-spk${RESET} (or ${CYAN}claude-shpak${RESET})  - Claude Code CLI"
echo -e "   • ${CYAN}codex-spk${RESET} (or ${CYAN}codex-shpak${RESET})   - OpenAI Codex CLI"
echo -e "   • ${CYAN}cursor-spk${RESET} (or ${CYAN}cursor-shpak${RESET})  - Cursor Agent CLI"
echo -e "2. In-session global hotkeys:"
echo -e "   • ${CYAN}Ctrl+T${RESET} - Direct Prompt: type in your language -> translates to English"
echo -e "   • ${CYAN}Ctrl+F${RESET} - Markdown Prompt: structures input into professional brief"
echo -e "   • ${CYAN}Ctrl+R${RESET} - Translate response (100% code and math preservation)"
echo -e "   • ${CYAN}Ctrl+Y${RESET} - Translate clipboard content"
echo -e "3. Management & configuration: run ${CYAN}spk${RESET} (or ${CYAN}shpak${RESET})"
echo -e "4. Test sandbox without accounts: run ${CYAN}agy-spk --demo${RESET} or ${CYAN}spk demo${RESET}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${RESET}"
