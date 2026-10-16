import os
import sys
import json
import shutil
from pathlib import Path

DEFAULT_PROMPT_TEMPLATE = """You are a technical prompt translator for an AI coding assistant.
Accurately translate the following developer prompt from {source_lang} to {target_lang}.

RULES:
1. Output ONLY the clean, translated technical prompt ready for direct execution by the coding agent.
2. Preserve all code blocks (```), inline code (`), command flags (--flag), paths, variable names, URLs, and technical terms exactly as-is.
3. Do not add quotes, markdown wrappers, conversational filler, or commentary.

INPUT PROMPT:
{text}"""

DEFAULT_FORMATTED_PROMPT_TEMPLATE = """You are an expert AI prompt engineer and technical translator.
Translate the following user request from {source_lang} to {target_lang} and structure it into a clean, high-quality Markdown prompt for an AI coding assistant.

RULES:
1. Translate accurately into professional technical English.
2. Structure the prompt into concise, well-organized Markdown sections:
   - ## Goal: Clear one-sentence objective
   - ## Requirements & Context: Specific constraints, technologies, or file targets
   - ## Key Implementation Steps: Bulleted technical actions
   - ## Acceptance Criteria: How to verify completion
3. Preserve all code blocks (```), identifiers, URLs, flags, and technical terms intact.
4. Output ONLY the resulting Markdown prompt ready to be executed by the coding agent (no conversational preamble or meta-commentary).

INPUT USER REQUEST:
{text}"""

DEFAULT_RESPONSE_TEMPLATE = """You are an expert technical translator specializing in software engineering, programming, and developer documentation.
Accurately translate the following agent response from {source_lang} to {target_lang}.

CRITICAL NON-NEGOTIABLE RULES:
1. STRICT COMPLETENESS & ZERO OMISSIONS: You must translate EVERY SINGLE paragraph, sentence, bullet point, table cell, and section from start to finish. You are strictly FORBIDDEN from summarizing, condensing, shortening, skipping, or omitting ANY content under any circumstances. Never use ellipses (...) to abbreviate text. Maintain strict 1-to-1 structural correspondence with the original text.
2. CODE & PLACEHOLDER PRESERVATION: NEVER alter, translate, or remove code inside markdown blocks (```...```), inline code (`...`), or placeholders (__CODE_BLOCK_X__, __INLINE_CODE_X__). Keep them exactly in their original locations.
3. IDENTIFIERS & PATHS: Keep variable names, function names, class names, file paths, git commands, and URLs exactly as-is.
4. EXACT MARKDOWN REPLICATION: Preserve all headers (#, ##, ###), tables (|), task lists ([ ], [x]), blockquotes and alerts (> [!NOTE], > [!TIP], > [!WARNING]), math formulas ($...$, $$...$$), details/summary tags (<details>, <summary>), and keyboard shortcuts (<kbd>) intact.
5. TERMINOLOGY: Use established technical terminology in the target language where natural, but preserve industry-standard English programming terms in context (e.g. "middleware", "endpoint", "pull request", "refactoring", "token").
6. PRESERVE MATH & UNICODE LAYOUTS: If mathematical expressions, matrices, ASCII tables, or diagrams are written in Unicode, plain text, or ASCII in the source, DO NOT convert or rewrite them into LaTeX blocks ($$ ... $$) or markdown tables. Keep Unicode math symbols and visual text layouts exactly as-is. If the original text contains LaTeX ($...$, $$...$$), keep the LaTeX equations and symbols strictly intact.
7. HYPERLINKS: Keep markdown hyperlinks in standard format [text](url) without expanding or duplicating URLs in parentheses.
8. CLEAN OUTPUT: Return ONLY the complete translated text, without commentary, conversational filler, or introductory notes.

TEXT TO TRANSLATE:
{text}"""

DEFAULT_CONFIG = {
    "version": "3.0.0",
    "onboarding_complete": False,
    "active_translator": {
        "provider": "agy-cli",
        "model": "gemini-3.8-flash-low"
    },
    "languages": {
        "target_response": "uk",
        "target_prompt": "en"
    },
    "copy_to_clipboard": False,
    "hotkeys": {
        "translate_prompt": "ctrl+t",
        "translate_prompt_formatted": "ctrl+f",
        "translate_response": "ctrl+r",
        "translate_clipboard": "ctrl+y"
    },
    "prompts": {
        "prompt": DEFAULT_PROMPT_TEMPLATE,
        "prompt_formatted": DEFAULT_FORMATTED_PROMPT_TEMPLATE,
        "response": DEFAULT_RESPONSE_TEMPLATE
    },
    "providers": {
        "agy-cli": {
            "type": "cli_subscription",
            "cli_tool": "agy",
            "default_model": "gemini-3.8-flash-low",
            "models": [
                "gemini-3.8-flash-low",
                "gemini-3.8-flash-medium",
                "gemini-3.8-flash-high",
                "claude-sonnet-5-5-low",
                "claude-sonnet-5-5-medium",
                "claude-sonnet-5-5-high",
                "claude-opus-5-5-low",
                "claude-opus-5-5-medium",
                "claude-opus-5-5-high",
                "gpt-oss-120b-medium"
            ],
            "description": "Antigravity CLI via active Google AI Pro subscription (Zero API keys needed!)"
        },
        "claude-cli": {
            "type": "cli_subscription",
            "cli_tool": "claude",
            "default_model": "haiku",
            "models": [
                "haiku",
                "sonnet",
                "opus"
            ],
            "description": "Claude Code CLI via active Claude subscription (Zero API keys needed!)"
        }
    }
}

CONFIG_DIR = Path.home() / ".config" / "shpak"
OLD_CONFIG_DIR = Path.home() / ".config" / "llm-translate"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOCAL_CONFIG_FILE = Path(__file__).parent.parent / "config.json"

def get_config_path() -> Path:
    if LOCAL_CONFIG_FILE.exists():
        return LOCAL_CONFIG_FILE
    if CONFIG_FILE.exists():
        return CONFIG_FILE
    if (OLD_CONFIG_DIR / "config.json").exists():
        return OLD_CONFIG_DIR / "config.json"
    return CONFIG_FILE

def get_prompt_template(cfg: dict, mode: str = "response") -> str:
    """Returns the dedicated prompt template for 'prompt', 'prompt_formatted', or 'response'."""
    prompts = cfg.get("prompts", {})
    if mode in ("prompt_formatted", "formatted"):
        return prompts.get("prompt_formatted") or DEFAULT_FORMATTED_PROMPT_TEMPLATE
    if mode in ("prompt", "direct"):
        return prompts.get("prompt") or DEFAULT_PROMPT_TEMPLATE
    return prompts.get("response") or DEFAULT_RESPONSE_TEMPLATE

def get_hotkeys(cfg: dict) -> dict:
    """Returns configured hotkeys."""
    return {
        "translate_prompt": cfg.get("hotkeys", {}).get("translate_prompt", "ctrl+t"),
        "translate_prompt_formatted": cfg.get("hotkeys", {}).get("translate_prompt_formatted", "ctrl+f"),
        "translate_response": cfg.get("hotkeys", {}).get("translate_response", "ctrl+r"),
        "translate_clipboard": cfg.get("hotkeys", {}).get("translate_clipboard", "ctrl+y")
    }

def load_config() -> dict:
    path = get_config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                merged = {**DEFAULT_CONFIG, **cfg}
                merged["hotkeys"] = {**DEFAULT_CONFIG["hotkeys"], **cfg.get("hotkeys", {})}
                merged["prompts"] = {**DEFAULT_CONFIG["prompts"], **cfg.get("prompts", {})}
                return merged
        except Exception as e:
            print(f"[Warning] Failed to read {path}: {e}. Using defaults.")
    return DEFAULT_CONFIG.copy()

def save_config(cfg: dict, global_config: bool = False):
    path = CONFIG_FILE if global_config else LOCAL_CONFIG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def detect_installed_agents() -> dict:
    """Scans system PATH for supported AI coding assistants."""
    agents = {
        "agy": {
            "name": "Google Antigravity",
            "cmd": "agy",
            "shpak_cmd": "agy-spk",
            "installed": False,
            "path": None,
            "desc": "Google AI Pro coding agent"
        },
        "claude": {
            "name": "Claude Code CLI",
            "cmd": "claude",
            "shpak_cmd": "claude-spk",
            "installed": False,
            "path": None,
            "desc": "Anthropic Claude Code CLI"
        },
        "codex": {
            "name": "OpenAI Codex CLI",
            "cmd": "codex",
            "shpak_cmd": "codex-spk",
            "installed": False,
            "path": None,
            "desc": "OpenAI Codex CLI assistant"
        },
        "cursor": {
            "name": "Cursor Agent",
            "cmd": "cursor-agent",
            "shpak_cmd": "cursor-spk",
            "installed": False,
            "path": None,
            "desc": "Cursor terminal coding agent"
        },
        "aider": {
            "name": "Aider",
            "cmd": "aider",
            "shpak_cmd": "spk aider",
            "installed": False,
            "path": None,
            "desc": "AI pair programming terminal tool"
        },
        "gemini": {
            "name": "Gemini CLI",
            "cmd": "gemini",
            "shpak_cmd": "spk gemini",
            "installed": False,
            "path": None,
            "desc": "Google Gemini CLI"
        }
    }

    for key, info in agents.items():
        found = shutil.which(info["cmd"])
        if not found and key == "cursor":
            found = shutil.which("cursor")
        if found:
            info["installed"] = True
            info["path"] = found

    return agents


BLUE_COLOR = "\033[38;5;39m\033[1m"
YELLOW_COLOR = "\033[38;5;220m\033[1m"
RESET = "\033[0m"

SPK_LOGO_LINES = [
    (BLUE_COLOR,   "        ▄▄██████▄▄                                        "),
    (BLUE_COLOR,   "       ▄████████████▄          ▄██████  ██████╗  ██╗  ██╗"),
    (BLUE_COLOR,   "      ███████▀▀███████        ███╔════╝ ██╔══██╗ ██║ ██╔╝"),
    (BLUE_COLOR,   "     ██████▀    ▀██████" + YELLOW_COLOR + "►" + BLUE_COLOR + "      ███████╗  ██████╔╝ █████═╝ "),
    (YELLOW_COLOR, "     ██████      ██████       ╚════███╗ ██╔═══╝  ██╔═██╗ "),
    (YELLOW_COLOR, "      ██████▄▄▄██████▀        ███████╔╝ ██║      ██║  ██╗"),
    (YELLOW_COLOR, "       ▀████████████▀         ╚══════╝  ╚═╝      ╚═╝  ╚═╝"),
    (YELLOW_COLOR, "         ▀▀██████▀▀                                       "),
]

def print_spk_logo():
    for col, line in SPK_LOGO_LINES:
        print(f"{col}{line}{RESET}")

def ensure_onboarding(cfg: dict, interactive: bool = True) -> dict:
    """Guides the user through initial language selection on the very first run."""
    if cfg.get("onboarding_complete", False):
        return cfg
    if not interactive or not sys.stdin.isatty():
        cfg["onboarding_complete"] = True
        return cfg

    CYAN = "\033[36m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BLUE_LINE = "\033[38;5;39m"
    YELLOW_LINE = "\033[38;5;220m"
    RESET = "\033[0m"

    print(f"\n{BLUE_LINE}─────────────────────────────────────────────────────────────{RESET}")
    print(f"  {BOLD}{WHITE}S H P A K{RESET}  {GRAY}│{RESET}  {CYAN}Initial Setup{RESET}")
    print(f"{YELLOW_LINE}─────────────────────────────────────────────────────────────{RESET}")
    print(f"Configure target translation languages for AI coding assistants:\n")

    popular_resp = [
        ("uk", "Ukrainian"),
        ("pl", "Polish"),
        ("de", "German"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("it", "Italian"),
        ("ja", "Japanese"),
        ("en", "English"),
    ]

    popular_prompt = [
        ("en", "English"),
        ("uk", "Ukrainian"),
        ("de", "German"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("ja", "Japanese"),
        ("zh", "Chinese"),
        ("pl", "Polish"),
    ]

    selected_resp = "uk"
    selected_prompt = "en"

    try:
        # Step 1: Response Language (Agent -> You)
        print(f"{BOLD}[1/2] Target Response Language (AI Agent ➔ You):{RESET}")
        for i in range(0, len(popular_resp), 2):
            c1, n1 = popular_resp[i]
            d1 = f" {GREEN}(default){RESET}" if c1 == "uk" else ""
            item1 = f"[{BOLD}{i+1}{RESET}] {c1.upper()}  {n1:<10}{d1}"
            if i + 1 < len(popular_resp):
                c2, n2 = popular_resp[i+1]
                item2 = f"[{BOLD}{i+2}{RESET}] {c2.upper()}  {n2:<10}"
                print(f"  {item1:<32} {item2}")
            else:
                print(f"  {item1}")
        print(f"  [{BOLD}C{RESET}] Custom ISO code (e.g. nl, tr, cs, pt)")

        choice_r = input(f"\n{BOLD}Select [1-{len(popular_resp)}, C, or Enter for Ukrainian]: {RESET}").strip()
        if choice_r.upper() == "C":
            custom = input(f"{BOLD}Enter 2-letter ISO code: {RESET}").strip().lower()
            selected_resp = custom if custom else "uk"
        elif choice_r:
            try:
                num = int(choice_r)
                if 1 <= num <= len(popular_resp):
                    selected_resp = popular_resp[num - 1][0]
                else:
                    selected_resp = "uk"
            except ValueError:
                selected_resp = choice_r.lower() if len(choice_r) <= 4 else "uk"

        # Step 2: Prompt Language (You -> Agent)
        print(f"\n{BOLD}[2/2] Target Prompt Language (You ➔ AI Agent):{RESET}")
        for i in range(0, len(popular_prompt), 2):
            c1, n1 = popular_prompt[i]
            d1 = f" {GREEN}(default){RESET}" if c1 == "en" else ""
            item1 = f"[{BOLD}{i+1}{RESET}] {c1.upper()}  {n1:<10}{d1}"
            if i + 1 < len(popular_prompt):
                c2, n2 = popular_prompt[i+1]
                item2 = f"[{BOLD}{i+2}{RESET}] {c2.upper()}  {n2:<10}"
                print(f"  {item1:<32} {item2}")
            else:
                print(f"  {item1}")
        print(f"  [{BOLD}C{RESET}] Custom ISO code")

        choice_p = input(f"\n{BOLD}Select [1-{len(popular_prompt)}, C, or Enter for English]: {RESET}").strip()
        if choice_p.upper() == "C":
            custom = input(f"{BOLD}Enter 2-letter ISO code: {RESET}").strip().lower()
            selected_prompt = custom if custom else "en"
        elif choice_p:
            try:
                num = int(choice_p)
                if 1 <= num <= len(popular_prompt):
                    selected_prompt = popular_prompt[num - 1][0]
                else:
                    selected_prompt = "en"
            except ValueError:
                selected_prompt = choice_p.lower() if len(choice_p) <= 4 else "en"

        cfg.setdefault("languages", {})["target_response"] = selected_resp
        cfg["languages"]["target_prompt"] = selected_prompt
        cfg["onboarding_complete"] = True
        save_config(cfg)

        print(f"\n{GREEN}✔ Configured:{RESET} Reply ➔ {BOLD}{selected_resp.upper()}{RESET} · Prompt ➔ {BOLD}{selected_prompt.upper()}{RESET}\n")
    except (KeyboardInterrupt, EOFError):
        cfg.setdefault("languages", {})["target_response"] = "uk"
        cfg.setdefault("languages", {})["target_prompt"] = "en"
        cfg["onboarding_complete"] = True
        save_config(cfg)

    return cfg
