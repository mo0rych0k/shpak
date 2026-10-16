#!/usr/bin/env bash
set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║        🐦 Installing Shpak (Шпак) AI CLI Suite             ║${RESET}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════╝${RESET}"

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

# Backward-compatible links
ln -sf agy-shpak "${INSTALL_DIR}/ag-tr" 2>/dev/null || true
ln -sf shpak-cli "${INSTALL_DIR}/tr" 2>/dev/null || true

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

# Backward compatibility in PATH
ln -sf "${INSTALL_DIR}/shpak-cli" "${BIN_DIR}/tr"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/ag-tr"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/claude-tr"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/codex-tr"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/cursor-tr"
ln -sf "${INSTALL_DIR}/agy-shpak" "${BIN_DIR}/llm-tr"

echo -e "   ${GREEN}✔ Symlinked spk & shpak to ${BIN_DIR}/spk${RESET}"
echo -e "   ${GREEN}✔ Symlinked agy-spk (або agy-shpak) to ${BIN_DIR}/agy-spk (Antigravity)${RESET}"
echo -e "   ${GREEN}✔ Symlinked claude-spk (або claude-shpak) to ${BIN_DIR}/claude-spk (Claude Code)${RESET}"
echo -e "   ${GREEN}✔ Symlinked codex-spk (або codex-shpak) to ${BIN_DIR}/codex-spk (Codex CLI)${RESET}"
echo -e "   ${GREEN}✔ Symlinked cursor-spk (або cursor-shpak) to ${BIN_DIR}/cursor-spk (Cursor Agent)${RESET}"

# 4. Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo -e "${YELLOW}⚠️  Note: ${BIN_DIR} is not in your current PATH.${RESET}"
    echo -e "   Add this line to your ${CYAN}~/.zshrc${RESET} or ${CYAN}~/.bashrc${RESET}:"
    echo -e "   ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
fi

echo ""
echo -e "${GREEN}🎉 Shpak (spk) успішно встановлено!${RESET}"
echo -e "────────────────────────────────────────────────────────────"
echo -e "1. Швидкий запуск AI-асистентів із прозорим перекладом:"
echo -e "   • ${CYAN}agy-spk${RESET} (або ${CYAN}agy-shpak${RESET})     - Antigravity CLI"
echo -e "   • ${CYAN}claude-spk${RESET} (або ${CYAN}claude-shpak${RESET})  - Claude Code CLI"
echo -e "   • ${CYAN}codex-spk${RESET} (або ${CYAN}codex-shpak${RESET})   - OpenAI Codex CLI"
echo -e "   • ${CYAN}cursor-spk${RESET} (або ${CYAN}cursor-shpak${RESET})  - Cursor Agent CLI"
echo -e "2. Гарячі клавіші у сесії:"
echo -e "   • ${CYAN}Ctrl+T${RESET} - Швидкий запит українською -> переклад на EN"
echo -e "   • ${CYAN}Ctrl+F${RESET} - Структурування у Markdown-промпт"
echo -e "   • ${CYAN}Ctrl+R${RESET} - Переклад відповіді агента (збереження коду 100%)"
echo -e "   • ${CYAN}Ctrl+Y${RESET} - Переклад вмісту буфера обміну"
echo -e "3. Керування та конфігурація: ${CYAN}spk${RESET} (або ${CYAN}shpak${RESET})"
echo -e "4. Тестовий режим без акаунтів: ${CYAN}agy-spk --demo${RESET} або ${CYAN}spk demo${RESET}"
echo -e "────────────────────────────────────────────────────────────"
