# 🐦 Shpak (`spk`)

> **Fast, transparent terminal PTY wrapper & technical prompt/response translator for AI coding assistants (Zero API Keys required).**

Like the **starling (Шпак)** bird, renowned for its incredible ability to mimic and master any voice or sound, **Shpak** allows developers worldwide to interact with terminal AI coding agents in their native language while guaranteeing 100% technical accuracy, flawless syntax preservation, and a completely native terminal experience.

Operates **without paid API keys**, routing translations through your existing active subscriptions (Google AI Pro via `agy` or Claude Pro via `claude`).

---

## ⚡ CLI Commands & Tools

Shpak provides ultra-fast 3-letter commands (`spk`) with full aliases (`shpak`):

| Command | Full Alias | Target Agent | Description |
| :--- | :--- | :--- | :--- |
| **`agy-spk`** | `agy-shpak` | **Google Antigravity** (`agy`) | Transparent PTY wrapper for Antigravity CLI |
| **`claude-spk`** | `claude-shpak` | **Claude Code CLI** (`claude`) | Transparent PTY wrapper for Anthropic Claude Code |
| **`codex-spk`** | `codex-shpak` | **OpenAI Codex CLI** (`codex`) | Transparent PTY wrapper for OpenAI Codex CLI |
| **`cursor-spk`** | `cursor-shpak` | **Cursor Agent** (`cursor-agent`) | Transparent PTY wrapper for Cursor terminal agent |
| **`spk`** | `shpak` | **Control Center & Manager** | Interactive TUI, agent detector, hotkey & prompt editor |

---

## 🚀 Installation

### Option 1: Quick One-Liner (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/mo0rych0k/shpak/main/install.sh | bash
```

### Option 2: Homebrew
```bash
brew install --HEAD https://raw.githubusercontent.com/mo0rych0k/shpak/main/Formula/shpak.rb
# Or via custom tap:
# brew install mo0rych0k/tap/shpak
```

### Option 3: Modern Python Package Manager (`uv` or `pipx`)
```bash
uv tool install git+https://github.com/mo0rych0k/shpak.git
# or
pipx install git+https://github.com/mo0rych0k/shpak.git
```

### Option 4: Manual Git Clone
```bash
git clone https://github.com/mo0rych0k/shpak.git
cd shpak
./install.sh
```

*(Ensure `~/.local/bin` is in your `$PATH`)*.

---

## 🌍 First-Launch Language Selection

On first launch, Shpak presents an interactive setup asking for your primary native language for AI responses:

```text
╔═══════════════════════════════════════════════════════════════╗
║                   🐦 Welcome to Shpak (spk)!                 ║
╚═══════════════════════════════════════════════════════════════╝
Please select your primary native language for AI agent responses:

  [1] UK   - Ukrainian
  [2] ES   - Spanish
  [3] DE   - German
  [4] FR   - French
  [5] PL   - Polish
  ...
```

You can change this anytime with `spk config --lang <code>` or inside the interactive menu (`spk`).

---

## 🤖 AI Agent Detection

Check which coding assistants are currently installed on your system:

```bash
spk agents
# or
spk status
```

Output:
```text
Detected AI Coding Assistants:
  • Google Antigravity  [agy-spk   ] : ✔ INSTALLED (/usr/local/bin/agy)
  • Claude Code CLI     [claude-spk] : ✔ INSTALLED (/usr/local/bin/claude)
  • OpenAI Codex CLI    [codex-spk ] : ✖ Not found in PATH
  • Cursor Agent        [cursor-spk] : ✖ Not found in PATH
  • Aider               [spk aider ] : ✖ Not found in PATH
```

---

## 🕹️ Global In-Session Hotkeys

All slash commands (`/`), Tab completion, arrow keys, history, and raw control sequences pass through **100% transparently**:

| Hotkey | Action | Description |
| :--- | :--- | :--- |
| **`Ctrl+T`** | 🌐 **Direct Prompt** | Pauses input, prompts for your native task description, translates to technical English, and injects clean text into the agent's input line. |
| **`Ctrl+F`** | 📝 **Markdown Prompt** | Translates and formats your request into a structured Markdown engineering brief (Goal, Requirements, Steps, Acceptance Criteria). |
| **`Ctrl+R`** | 📜 **Translate Response** | Extracts latest assistant response from session logs, translates to your selected language with **CodeShield** protection, renders in terminal, and copies to clipboard. |
| **`Ctrl+Y`** | 📋 **Clipboard Translation** | Reads copied text from system clipboard (e.g. Jira ticket or browser snippet), translates to technical English, and injects it into the session. |

---

## 💡 Usage Examples

### 1. Launch Antigravity with Translation Wrapper
```bash
agy-spk

# Or directly with an initial task in your native language:
agy-spk "create an asynchronous HTTP server in FastAPI with JWT authentication"
```

### 2. Launch Claude Code CLI
```bash
claude-spk

# With an initial task:
claude-spk "refactor error handling in the payment service"
```

### 3. Launch Codex CLI
```bash
codex-spk
```

### 4. Interactive Demo Sandbox (Zero Accounts Needed)
Want to test all hotkeys right now without external CLI logins?
```bash
agy-spk --demo
# or
spk demo
```

---

## 🛠️ Control Center (`spk`)

Launch the interactive management console:
```bash
spk
```

Features:
- **Switch translation provider**: `agy-cli` (Google AI Pro) or `claude-cli` (Claude Pro).
- **Model selector**: `gemini-3.8-flash-low`, `haiku`, `sonnet`, etc.
- **Language configuration**: Ukrainian, Spanish, German, French, Polish, Japanese, etc.
- **Hotkey manager**: customize shortcut keys (`spk hotkeys`).
- **Prompt rules editor**: edit system prompts for direct and Markdown translation (`spk rules`).
- **Agent launcher**: view detected agents and launch immediately.
- **Auto-updater**: pull updates via `spk update`.

---

## 🛡️ CodeShield Technology

Response translation is safeguarded by **CodeShield**:
* Fenced code blocks (````...````) and inline code (`` `...` ``) are shielded with AST placeholders and never altered.
* File paths, identifiers, class names, variable names, and git flags remain intact.
* Mathematical formulas in KaTeX, LaTeX display blocks, and ASCII/Unicode math matrices retain exact visual structure.
* Repeated translation queries return in 0.01s from cache.

---

## 📄 License

MIT License. Designed with ❤️ in Ukraine.
