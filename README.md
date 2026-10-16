# 🐦 Shpak (`spk`)

<p align="center">
  <b>English</b> | <a href="README.uk.md"><b>Українська</b></a>
</p>

> **Fast, transparent terminal PTY wrapper & technical prompt/response translator for AI coding assistants (Zero API Keys required).**

<p align="center">
  <img src="assets/shpak-tui.png" alt="Shpak Interactive TUI Control Center" width="750">
</p>

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
🐦 shpak initial setup
─────────────────────────────────────────────────────────────
Configure target translation languages for AI coding assistants:

[1/2] Target Response Language (AI Agent ➔ You):
  [1] UK  Ukrainian (default)    [2] PL  Polish
  [3] DE  German                 [4] ES  Spanish
  [5] FR  French                 [6] IT  Italian
  [7] JA  Japanese               [8] EN  English
  [C] Custom ISO code (e.g. nl, tr, cs, pt)
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

Launch the unified interactive management console at any time by typing:
```bash
spk
```

<p align="center">
  <img src="assets/shpak-tui.png" alt="Shpak TUI Control Center Menu" width="700">
</p>

The TUI provides real-time visibility into your translation environment without editing config files manually:

* **Live Status Header**: Displays the current translator backend (`agy-cli` / `claude-cli`), active model (`gemini-3.8-flash-low`, `haiku`, etc.), prompt auto-translation state (`ON`/`OFF`), source/target languages, proxy port, and registered hotkeys.
* **Configuration Menu `[1-6]`**:
  * `[1]` Toggle active agent between Google Antigravity and Claude Code.
  * `[2]` Select translation model profile (fast latency vs deep reasoning).
  * `[3]` Change target response language (`UK`, `PL`, `DE`, `ES`, `FR`, `IT`, `JA`, `EN`, or custom ISO code).
  * `[4]` Change prompt translation language.
  * `[5]` Customize global session hotkeys (`Ctrl+T`, `Ctrl+F`, `Ctrl+R`, `Ctrl+Y`).
  * `[6]` Fine-tune system prompt engineering rules for technical translations.
* **Operations & Agents `[7-0]`**:
  * `[7]` Directly launch your configured AI coding assistant session with transparent translation.
  * `[8]` Open the **Demo Sandbox** to experiment with prompt & response translation without logging into any CLI tool.
  * `[9]` Run system diagnostics to discover which AI coding CLIs are installed and on your `$PATH`.
  * `[U]` Check for and pull updates to the latest Shpak release.
  * `[0]` Exit safely.

---

## 🛡️ CodeShield Technology

Response translation is safeguarded by **CodeShield**:
* Fenced code blocks (````...````) and inline code (`` `...` ``) are shielded with AST placeholders and never altered.
* File paths, identifiers, class names, variable names, and git flags remain intact.
* Mathematical formulas in KaTeX, LaTeX display blocks, and ASCII/Unicode math matrices retain exact visual structure.
* Repeated translation queries return in 0.01s from cache.

---

## 🗑️ Uninstallation

To remove Shpak completely from your system (including binaries, configuration, and cache for a 100% clean reset):

### Quick One-Liner
```bash
curl -fsSL https://raw.githubusercontent.com/mo0rych0k/shpak/main/uninstall.sh | bash
```

### Or Manual Wipe
```bash
# 1. Remove CLI symlinks
rm -f ~/.local/bin/spk ~/.local/bin/shpak ~/.local/bin/*-spk ~/.local/bin/*-shpak

# 2. Remove configuration and caches (resets zero-state onboarding)
rm -rf ~/.config/shpak ~/.config/llm-translate ~/.cache/shpak

# 3. Remove remote cloned repository if installed via curl
rm -rf ~/.shpak
```

---

## 📄 License

[MIT License](LICENSE). Designed with ❤️ in Ukraine.
