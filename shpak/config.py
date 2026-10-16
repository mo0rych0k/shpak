import os
import json
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
5. TERMINOLOGY: Use established Ukrainian tech terminology where natural (e.g. "розгортання", "перехоплення", "обробник"), but leave industry-standard English terms in context (e.g. "middleware", "endpoint", "pull request", "refactoring").
6. PRESERVE MATH & UNICODE LAYOUTS: If mathematical expressions, matrices, ASCII tables, or diagrams are written in Unicode, plain text, or ASCII in the source, DO NOT convert or rewrite them into LaTeX blocks ($$ ... $$) or markdown tables. Keep Unicode math symbols and visual text layouts exactly as-is. If the original text contains LaTeX ($...$, $$...$$), keep the LaTeX equations and symbols strictly intact.
7. HYPERLINKS: Keep markdown hyperlinks in standard format [text](url) without expanding or duplicating URLs in parentheses.
8. CLEAN OUTPUT: Return ONLY the complete translated text, without commentary, conversational filler, or introductory notes.

TEXT TO TRANSLATE:
{text}"""

DEFAULT_CONFIG = {
    "version": "3.0.0",
    "active_translator": {
        "provider": "agy-cli",
        "model": "gemini-3.8-flash-low"
    },
    "languages": {
        "target_response": "uk",
        "target_prompt": "en"
    },
    "copy_to_clipboard": True,
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
