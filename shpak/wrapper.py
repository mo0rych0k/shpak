#!/usr/bin/env python3
"""
Shpak: Zero-Glitches Transparent PTY Wrapper for AI Coding CLIs (Antigravity, Claude Code, Codex, Cursor Agent, etc.)
No API keys required - uses active AI subscriptions for translation!
"""

import os
import sys
import pty
import tty
import termios
import select
import signal
import fcntl
import json
import time
import shutil
import re
import subprocess
import atexit
from pathlib import Path

ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

HOTKEY_BYTE_MAP = {
    "ctrl+a": b"\x01",
    "ctrl+b": b"\x02",
    "ctrl+d": b"\x04",
    "ctrl+e": b"\x05",
    "ctrl+f": b"\x06",
    "ctrl+g": b"\x07",
    "ctrl+k": b"\x0b",
    "ctrl+l": b"\x0c",
    "ctrl+n": b"\x0e",
    "ctrl+p": b"\x10",
    "ctrl+r": b"\x12",
    "ctrl+t": b"\x14",
    "ctrl+u": b"\x15",
    "ctrl+w": b"\x17",
    "ctrl+x": b"\x18",
    "ctrl+y": b"\x19",
}

def get_clipboard_text() -> str:
    """Safely extracts current text from clipboard across platforms."""
    if sys.platform == "darwin":
        try:
            return subprocess.check_output(["pbpaste"], text=True).strip()
        except Exception:
            return ""
    elif shutil.which("xclip"):
        try:
            return subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True).strip()
        except Exception:
            return ""
    return ""

def get_translator_info() -> tuple:
    """Returns (tool_name, model_name)."""
    try:
        sys.path.insert(0, ROOT_DIR)
        from .config import load_config
        cfg = load_config()
        active = cfg.get("active_translator", {})
        provider = active.get("provider", "agy-cli")
        model = active.get("model", "gemini-3.8-flash-low")
        name = "agy" if "agy" in provider else ("claude" if "claude" in provider else provider)
        return name, model
    except Exception:
        return "agy", "gemini-3.8-flash-low"

def translate_prompt_local(text: str, mode: str = "prompt") -> str:
    """Translates text using the configured provider in config.json and the chosen prompt mode."""
    cleaned = re.sub(r'^/(?:tr|translate)\s*', '', text.strip())
    if not cleaned:
        return text

    # 1. Try unified configuration from shpak
    target_lang = "uk" if mode == "response" else "en"
    try:
        sys.path.insert(0, ROOT_DIR)
        from .config import load_config
        from .translator.factory import create_translator
        cfg = load_config()
        translator = create_translator(cfg)
        lang_cfg = cfg.get("languages", {})
        if mode == "response":
            target_lang = lang_cfg.get("target_response", "uk")
        else:
            target_lang = lang_cfg.get("target_prompt", "en")
        translated = translator.translate(cleaned, source_lang="auto", target_lang=target_lang, mode=mode)
        if translated and translated.strip():
            return translated.strip()
    except Exception:
        pass

    # 2. Fallback to direct agy CLI
    try:
        from .translator.base import get_language_name
        target_name = get_language_name(target_lang)
    except Exception:
        target_name = target_lang

    if mode == "response":
        instruction = (
            f"Translate the following AI coding assistant response to {target_name} ({target_lang.upper()}). "
            "Translate 100% completely without skipping, condensing, or omitting anything. "
            "Preserve all code blocks, inline code, math formulas, and markdown formatting intact. "
            "Return ONLY the translated text without conversational filler:\n\n" + cleaned
        )
    else:
        instruction = (
            f"Translate the following user instruction to natural, precise technical {target_name} ({target_lang.upper()}) "
            "for an AI coding assistant. Translate 100% completely without skipping, condensing, "
            "or omitting anything. Return ONLY the translated text without markdown quotes, "
            "preambles, or conversational filler:\n\n" + cleaned
        )

    agy_bin = shutil.which("antigravity") or shutil.which("agy") or "agy"
    try:
        proc = subprocess.run(
            [agy_bin, "--disable-slash-commands", "--model", "gemini-3.8-flash-low", "-p", instruction],
            capture_output=True,
            text=True,
            timeout=15
        )
        if proc.returncode == 0 and proc.stdout.strip():
            out = proc.stdout.strip()
            if (out.startswith('"') and out.endswith('"')) or (out.startswith("'") and out.endswith("'")):
                out = out[1:-1].strip()
            return out
    except Exception as e:
        sys.stderr.write(f"\r\n[shpak backend warning: {e}]\r\n")

    return cleaned

_RESPONSE_CACHE = {"raw": "", "translated": "", "lang": "uk"}

def translate_response_local(since_time: float = None, target_tool: str = "auto") -> tuple:
    """Fetches the latest agent response and translates it to target response language via isolated subprocess."""
    global _RESPONSE_CACHE
    try:
        from .reader import get_latest_agent_response
        current_raw = get_latest_agent_response(target=target_tool, since_time=since_time)
        if current_raw and current_raw == _RESPONSE_CACHE["raw"] and _RESPONSE_CACHE["translated"]:
            return _RESPONSE_CACHE["translated"], _RESPONSE_CACHE["lang"]
    except Exception:
        current_raw = None

    runner = f"""
import sys, json, os
sys.path.insert(0, {repr(ROOT_DIR)})
try:
    from shpak.config import load_config
    from shpak.translator.factory import create_translator
    from shpak.reader import get_latest_agent_response
except ImportError:
    from llm_translate.config import load_config
    from llm_translate.translator.factory import create_translator
    from llm_translate.reader import get_latest_agent_response

raw_text = get_latest_agent_response(target={repr(target_tool)}, since_time={since_time})
if not raw_text:
    print(json.dumps({{"translated": "", "lang": ""}}))
    sys.exit(0)

cfg = load_config()
target_resp = cfg.get("languages", {{}}).get("target_response", "uk")
translator = create_translator(cfg)
translated = translator.translate(raw_text, source_lang="auto", target_lang=target_resp, mode="response")
print(json.dumps({{"translated": translated, "lang": target_resp}}))
"""
    try:
        env = dict(os.environ)
        env["PYTHONPATH"] = f"{ROOT_DIR}:{env.get('PYTHONPATH', '')}"
        proc = subprocess.run(
            [sys.executable, "-c", runner],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180,
            env=env
        )
        if proc.returncode == 0 and proc.stdout.strip():
            res = json.loads(proc.stdout.strip())
            tr = res.get("translated", "")
            lg = res.get("lang", "uk")
            if tr:
                _RESPONSE_CACHE["raw"] = current_raw or ""
                _RESPONSE_CACHE["translated"] = tr
                _RESPONSE_CACHE["lang"] = lg
            return tr, lg
        elif proc.stderr.strip():
            sys.stderr.write(f"\r\n[shpak backend error: {proc.stderr.strip()}]\r\n")
    except Exception as e:
        sys.stderr.write(f"\r\n[shpak translation error: {e}]\r\n")

    return "", ""

def set_pty_size(master_fd: int):
    """Sync parent terminal dimensions to slave PTY."""
    try:
        fd = sys.stdin.fileno() if sys.stdin.isatty() else sys.stdout.fileno()
        winsize = fcntl.ioctl(fd, termios.TIOCGWINSZ, b"\x00" * 8)
        fcntl.ioctl(master_fd, termios.TIOCSWINSZ, winsize)
    except Exception:
        pass

def run_demo_agent():
    """Built-in interactive demo agent running inside child PTY for instant testing."""
    import tempfile
    session_file = Path(tempfile.gettempdir()) / "llm_tr_demo_session.txt"
    initial_msg = (
        "Hello! I am a simulated AI coding assistant.\n\n"
        "Here is an example response with code and markdown formatting:\n\n"
        "```python\n"
        "def calculate_metrics(values: list[float]) -> dict:\n"
        "    return {\n"
        "        'avg': sum(values) / len(values) if values else 0.0,\n"
        "        'peak': max(values) if values else 0.0\n"
        "    }\n"
        "```\n\n"
        "| Step | Action | Status |\n"
        "| :--- | :--- | :--- |\n"
        "| 1 | Validate input parameters | ✅ Completed |\n"
        "| 2 | Compute statistical summary | ⚡ In progress |\n"
        "| 3 | Export report | ⏳ Pending |\n\n"
        "> [!TIP]\n"
        "> Press **Ctrl+R** right now to test translating this response into Ukrainian!"
    )
    try:
        session_file.write_text(initial_msg, encoding="utf-8")
    except Exception:
        pass

    sys.stdout.write("\r\n\033[38;5;39m─────────────────────────────────────────────────────────────\033[0m\r\n")
    sys.stdout.write("  \033[1;97mS H P A K\033[0m  \033[90m│\033[0m  \033[36mDemo Simulator\033[0m  \033[90m·  testing playground\033[0m\r\n")
    sys.stdout.write("\033[38;5;220m─────────────────────────────────────────────────────────────\033[0m\r\n")
    sys.stdout.write("  \033[90mHotkeys:\033[0m \033[1;33mCtrl+T\033[0m (Prompt) · \033[1;35mCtrl+F\033[0m (Markdown) · \033[1;32mCtrl+R\033[0m (Reply) · \033[1;36mCtrl+Y\033[0m (Clip)\r\n")
    sys.stdout.write("  \033[90m(Type 'exit' to quit)\033[0m\r\n\r\n")

    sys.stdout.write(initial_msg.replace("\n", "\r\n") + "\r\n\r\n")
    sys.stdout.flush()

    while True:
        try:
            sys.stdout.write("\033[1;32muser> \033[0m")
            sys.stdout.flush()
            user_input = sys.stdin.readline()
            if not user_input:
                break
            user_input = user_input.strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        reply = (
            f"Thank you for your prompt: \"{user_input}\".\n\n"
            "Here is the generated output:\n"
            "```bash\n"
            f"# Running automated task\n"
            f"echo 'Processing: {user_input}'\n"
            "```\n\n"
            "Everything was executed cleanly! Press `Ctrl+R` to translate this reply."
        )
        try:
            session_file.write_text(reply, encoding="utf-8")
        except Exception:
            pass
        sys.stdout.write("\r\n\033[1;34massistant> \033[0m" + reply.replace("\n", "\r\n") + "\r\n\r\n")
        sys.stdout.flush()

def resolve_target_info() -> dict:
    """
    Detects target tool and arguments from:
    1. Executable name (sys.argv[0]): agy-shpak, claude-shpak, codex-shpak, cursor-shpak, shpak
    2. Explicit flags: --target=<tool> or -t <tool>, or --demo
    3. For shpak run: first argument is the tool name (e.g. `shpak claude`)
    """
    invoked_name = Path(sys.argv[0]).stem.lower()
    cli_args = list(sys.argv[1:])

    # Check for demo mode flag
    is_demo = False
    if "--demo" in cli_args or "-d" in cli_args:
        is_demo = True
        cli_args = [a for a in cli_args if a not in ("--demo", "-d")]

    # 1. Check for --target or -t flag
    explicit_target = None
    filtered_args = []
    i = 0
    while i < len(cli_args):
        arg = cli_args[i]
        if arg.startswith("--target="):
            explicit_target = arg.split("=", 1)[1].strip()
        elif arg in ("--target", "-t"):
            if i + 1 < len(cli_args):
                explicit_target = cli_args[i + 1].strip()
                i += 1
        else:
            filtered_args.append(arg)
        i += 1
    cli_args = filtered_args

    # 2. Determine tool identifier
    tool_id = "agy"
    if is_demo or explicit_target in ("demo", "test") or "demo" in invoked_name:
        tool_id = "demo"
    elif explicit_target:
        tool_id = explicit_target.lower()
    elif "claude" in invoked_name:
        tool_id = "claude"
    elif "codex" in invoked_name:
        tool_id = "codex"
    elif "cursor" in invoked_name:
        tool_id = "cursor"
    elif "aider" in invoked_name:
        tool_id = "aider"
    elif "shpak" in invoked_name or "spk" in invoked_name or "llm" in invoked_name:
        if cli_args:
            first = cli_args[0].lower()
            if first in ("demo", "test"):
                tool_id = "demo"
                cli_args = cli_args[1:]
            elif first in ("claude", "codex", "agy", "antigravity", "cursor", "cursor-agent", "aider") or shutil.which(cli_args[0]):
                tool_id = first
                cli_args = cli_args[1:]
            else:
                tool_id = "agy"
        else:
            tool_id = "agy"
    else:
        tool_id = "agy"

    prefer_spk = "spk" in invoked_name or invoked_name in ("spk", "agy-spk", "claude-spk", "codex-spk", "cursor-spk", "aider-spk")
    s_suffix = "spk" if prefer_spk else "shpak"

    # Map tool_id to target binary, display tags, and session reader ID
    if tool_id == "demo":
        target_bin = sys.executable
        display_tag = f"{s_suffix}-demo"
        app_name = "Demo Agent"
        reader_id = "demo"
        cli_args = []
    elif tool_id in ("claude", "claude-code", "claude-cli"):
        target_bin = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude") or "claude"
        display_tag = f"claude-{s_suffix}"
        app_name = "Claude Code"
        reader_id = "claude"
    elif tool_id in ("codex", "codex-cli"):
        target_bin = shutil.which("codex") or str(Path.home() / ".local" / "bin" / "codex") or "codex"
        display_tag = f"codex-{s_suffix}"
        app_name = "Codex CLI"
        reader_id = "codex"
    elif tool_id in ("cursor", "cursor-agent", "agent"):
        target_bin = shutil.which("cursor-agent") or shutil.which("agent") or str(Path.home() / ".local" / "bin" / "cursor-agent") or "cursor-agent"
        display_tag = f"cursor-{s_suffix}"
        app_name = "Cursor Agent"
        reader_id = "auto"
    elif tool_id in ("aider",):
        target_bin = shutil.which("aider") or "aider"
        display_tag = f"aider-{s_suffix}"
        app_name = "Aider"
        reader_id = "aider"
    elif tool_id in ("agy", "antigravity", "ag"):
        for cand in ["antigravity", "agy", str(Path.home() / ".local" / "bin" / "agy")]:
            found = shutil.which(cand)
            if found:
                target_bin = found
                break
        else:
            target_bin = "agy"
        display_tag = f"agy-{s_suffix}"
        app_name = "Antigravity"
        reader_id = "antigravity"
    else:
        target_bin = shutil.which(tool_id) or tool_id
        display_tag = f"{tool_id}-{s_suffix}"
        app_name = tool_id.capitalize()
        reader_id = "auto"

    return {
        "tool_id": tool_id,
        "binary": target_bin,
        "display_tag": display_tag,
        "app_name": app_name,
        "reader_id": reader_id,
        "args": cli_args
    }

def read_translation_line() -> str:
    """Reads a line of text in raw mode with support for backspace, UTF-8, paste (Cmd+V, Ctrl+V, Alt+V), and cancel."""
    line = ""
    in_bracketed_paste = False
    while True:
        r, _, _ = select.select([sys.stdin.fileno()], [], [])
        if sys.stdin.fileno() in r:
            try:
                ch = os.read(sys.stdin.fileno(), 4096)
            except OSError:
                return ""
            if not ch:
                return ""

            # 1. Cancel on Ctrl+C
            if b"\x03" in ch:
                os.write(sys.stdout.fileno(), " \033[90m(cancelled)\033[0m\r\n".encode("utf-8"))
                return ""

            # 2. Bracketed paste markers (Cmd+V in modern terminals)
            if b"\x1b[200~" in ch:
                in_bracketed_paste = True
                ch = ch.replace(b"\x1b[200~", b"")
            if b"\x1b[201~" in ch:
                in_bracketed_paste = False
                ch = ch.replace(b"\x1b[201~", b"")

            # 3. Explicit paste hotkeys: Ctrl+V (0x16) or Alt+V (\x1bv / \x1bV)
            if ch in (b"\x16", b"\x1bv", b"\x1bV"):
                clip = get_clipboard_text()
                if clip:
                    clean_clip = clip.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
                    line += clean_clip
                    os.write(sys.stdout.fileno(), clean_clip.encode("utf-8"))
                continue

            # 4. Check for escape sequences vs standalone Escape key
            if ch == b"\x1b":
                r_more, _, _ = select.select([sys.stdin.fileno()], [], [], 0.05)
                if r_more:
                    try:
                        more_ch = os.read(sys.stdin.fileno(), 1024)
                        ch += more_ch
                    except OSError:
                        pass

                if ch == b"\x1b":
                    os.write(sys.stdout.fileno(), " \033[90m(cancelled)\033[0m\r\n".encode("utf-8"))
                    return ""

                if ch in (b"\x1bv", b"\x1bV"):
                    clip = get_clipboard_text()
                    if clip:
                        clean_clip = clip.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
                        line += clean_clip
                        os.write(sys.stdout.fileno(), clean_clip.encode("utf-8"))
                    continue

            # 5. Ignore other ANSI escape sequences (arrows, home, end, etc.)
            if ch.startswith(b"\x1b[") or ch.startswith(b"\x1bO"):
                continue

            # 6. Enter key
            if (b"\r" in ch or b"\n" in ch) and not in_bracketed_paste:
                os.write(sys.stdout.fileno(), b"\r\n")
                return line.strip()

            # 7. Backspace / Delete
            if b"\x7f" in ch or b"\x08" in ch:
                if line:
                    line = line[:-1]
                    os.write(sys.stdout.fileno(), b"\b \b")
                continue

            # 8. Printable characters (including pasted text)
            try:
                decoded = ch.decode("utf-8", errors="ignore")
                if in_bracketed_paste:
                    decoded = decoded.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
                line += decoded
                os.write(sys.stdout.fileno(), decoded.encode("utf-8"))
            except Exception:
                pass

def main():
    session_start_time = time.time()

    sys.path.insert(0, ROOT_DIR)
    from .config import load_config, get_hotkeys
    cfg = load_config()
    hotkeys = get_hotkeys(cfg)

    hk_prompt_str = hotkeys.get("translate_prompt", "ctrl+t").lower()
    hk_prompt_fmt_str = hotkeys.get("translate_prompt_formatted", "ctrl+f").lower()
    hk_resp_str = hotkeys.get("translate_response", "ctrl+r").lower()
    hk_clip_str = hotkeys.get("translate_clipboard", "ctrl+y").lower()

    byte_prompt = HOTKEY_BYTE_MAP.get(hk_prompt_str, b"\x14")
    byte_prompt_fmt = HOTKEY_BYTE_MAP.get(hk_prompt_fmt_str, b"\x06")
    byte_resp = HOTKEY_BYTE_MAP.get(hk_resp_str, b"\x12")
    byte_clip = HOTKEY_BYTE_MAP.get(hk_clip_str, b"\x19")

    target_info = resolve_target_info()
    display_tag = target_info["display_tag"]
    app_name = target_info["app_name"]
    reader_id = target_info["reader_id"]
    cli_args = list(target_info["args"])

    # If initial prompt argument was provided on command line, translate it first
    if cli_args and not cli_args[0].startswith("-"):
        raw_prompt = " ".join(cli_args)
        t_name, m_name = get_translator_info()
        print(f"🐦 [{display_tag}]: [{t_name}: {m_name}] translating initial prompt...")
        initial_translated_prompt = translate_prompt_local(raw_prompt)
        print(f"⚡ [{display_tag} -> EN]: {initial_translated_prompt}\n")

        # Specific CLI flag formatting
        if target_info["tool_id"] in ("agy", "antigravity"):
            cmd = [target_info["binary"], "-i", initial_translated_prompt]
        else:
            cmd = [target_info["binary"], initial_translated_prompt]
    else:
        cmd = [target_info["binary"]] + cli_args

    # Spawn child inside a true POSIX controlling terminal using pty.fork()
    pid, master_fd = pty.fork()
    if pid == 0:
        # --- CHILD PROCESS ---
        if target_info["tool_id"] == "demo":
            try:
                run_demo_agent()
            except Exception:
                pass
            sys.exit(0)

        try:
            os.execvp(cmd[0], cmd)
        except Exception as e:
            sys.stderr.write(f"\r\n[{display_tag}] Exec error launching {cmd[0]}: {e}\r\n")
            sys.exit(1)

    # --- PARENT PROCESS ---
    set_pty_size(master_fd)

    def handle_sigwinch(signum, frame):
        set_pty_size(master_fd)
        try:
            os.kill(pid, signal.SIGWINCH)
            pgid = os.getpgid(pid)
            if pgid != os.getpgrp():
                os.killpg(pgid, signal.SIGWINCH)
        except OSError:
            pass

    signal.signal(signal.SIGWINCH, handle_sigwinch)

    orig_termios = termios.tcgetattr(sys.stdin.fileno())

    def restore_terminal():
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, orig_termios)
        except Exception:
            pass

    atexit.register(restore_terminal)
    tty.setraw(sys.stdin.fileno())

    # Dynamic banner hint
    hint = (
        f"\r\n\033[90m[{display_tag}]: \033[1;36m{hk_prompt_str.upper()}\033[0;90m — Prompt | "
        f"\033[1;35m{hk_prompt_fmt_str.upper()}\033[0;90m — Markdown | "
        f"\033[1;36m{hk_resp_str.upper()}\033[0;90m — Response | "
        f"\033[1;36m{hk_clip_str.upper()}\033[0;90m — Clipboard\033[0m\r\n"
    ).encode("utf-8")
    os.write(sys.stdout.fileno(), hint)

    last_copied_response = ""
    terminal_screen_buffer = []

    try:
        while True:
            child_pid, status = os.waitpid(pid, os.WNOHANG)
            if child_pid == pid:
                break

            rlist, _, _ = select.select([sys.stdin.fileno(), master_fd], [], [], 0.05)

            # 1. Output from Target CLI -> Terminal stdout (100% direct, zero buffering)
            if master_fd in rlist:
                try:
                    out = os.read(master_fd, 4096)
                    if not out:
                        break
                    os.write(sys.stdout.fileno(), out)
                    try:
                        terminal_screen_buffer.append(out.decode("utf-8", errors="ignore"))
                        if len(terminal_screen_buffer) > 300:
                            terminal_screen_buffer = terminal_screen_buffer[-150:]
                    except Exception:
                        pass
                except OSError:
                    break

            # 2. Input from Terminal stdin -> Target CLI
            if sys.stdin.fileno() in rlist:
                try:
                    chunk = os.read(sys.stdin.fileno(), 1024)
                    if not chunk:
                        break
                except OSError:
                    break

                # 1. Direct Prompt Translation Hotkey (Ctrl+T)
                if byte_prompt in chunk:
                    prompt_header = f"\r\n\033[1;36m🐦 [{display_tag} {hk_prompt_str.upper()} Prompt Translator]:\033[0m ".encode("utf-8")
                    os.write(sys.stdout.fileno(), prompt_header)

                    user_text = read_translation_line()
                    if user_text:
                        t_name, m_name = get_translator_info()
                        prompt_lang = cfg.get("languages", {}).get("target_prompt", "en")
                        try:
                            from .translator.base import get_language_name
                            prompt_lang_name = get_language_name(prompt_lang)
                        except Exception:
                            prompt_lang_name = prompt_lang.upper()
                        os.write(sys.stdout.fileno(), f"\033[90m[{t_name}: {m_name}] translating prompt to {prompt_lang_name} ({prompt_lang.upper()})...\033[0m\r".encode("utf-8"))
                        try:
                            translated = translate_prompt_local(user_text, mode="prompt")
                            os.write(sys.stdout.fileno(), b"\033[2K\r")
                            marker = f"\033[1;32m⚡ [{display_tag} -> {prompt_lang.upper()}]:\033[0m {translated}\r\n".encode("utf-8")
                            os.write(sys.stdout.fileno(), marker)
                            # Inject clean prompt into child process
                            if "\n" in translated:
                                paste_payload = f"\033[200~{translated}\033[201~\r"
                            else:
                                paste_payload = f"{translated}\r"
                            os.write(master_fd, paste_payload.encode("utf-8"))
                        except Exception as e:
                            os.write(sys.stdout.fileno(), f"\r\n\033[31m[Translation error: {e}]\033[0m\r\n".encode("utf-8"))
                            os.write(master_fd, (user_text + "\r").encode("utf-8"))
                    continue

                # 2. Formatted Markdown Prompt Hotkey (Ctrl+F)
                if byte_prompt_fmt in chunk:
                    prompt_header = f"\r\n\033[1;35m📝 [{display_tag} {hk_prompt_fmt_str.upper()} Markdown Formatter]:\033[0m ".encode("utf-8")
                    os.write(sys.stdout.fileno(), prompt_header)

                    user_text = read_translation_line()
                    if user_text:
                        t_name, m_name = get_translator_info()
                        prompt_lang = cfg.get("languages", {}).get("target_prompt", "en")
                        try:
                            from .translator.base import get_language_name
                            prompt_lang_name = get_language_name(prompt_lang)
                        except Exception:
                            prompt_lang_name = prompt_lang.upper()
                        os.write(sys.stdout.fileno(), f"\033[90m[{t_name}: {m_name}] formatting Markdown prompt in {prompt_lang_name} ({prompt_lang.upper()})...\033[0m\r".encode("utf-8"))
                        try:
                            translated = translate_prompt_local(user_text, mode="prompt_formatted")
                            os.write(sys.stdout.fileno(), b"\033[2K\r")
                            marker = f"\033[1;35m⚡ [{display_tag} -> {prompt_lang.upper()} Markdown Prompt]:\033[0m\r\n{translated}\r\n".encode("utf-8")
                            os.write(sys.stdout.fileno(), marker)
                            # Inject clean formatted prompt into child process with bracketed paste
                            paste_payload = f"\033[200~{translated}\033[201~\r"
                            os.write(master_fd, paste_payload.encode("utf-8"))
                        except Exception as e:
                            os.write(sys.stdout.fileno(), f"\r\n\033[31m[Formatting error: {e}]\033[0m\r\n".encode("utf-8"))
                            os.write(master_fd, (user_text + "\r").encode("utf-8"))
                    continue

                # 3. Response Translation Hotkey (Ctrl+R / Ctrl+U)
                if byte_resp in chunk or b"\x15" in chunk:
                    t_name, m_name = get_translator_info()
                    target_resp = cfg.get("languages", {}).get("target_response", "uk")
                    try:
                        from .translator.base import get_language_name
                        resp_lang_name = get_language_name(target_resp)
                    except Exception:
                        resp_lang_name = target_resp.upper()
                    os.write(sys.stdout.fileno(), f"\r\n\033[1;36m🐦 [{display_tag}]:\033[0m \033[90m[{t_name}: {m_name}] translating {app_name} response to {resp_lang_name} ({target_resp.upper()})...\033[0m\r\n".encode("utf-8"))
                    try:
                        translated, target_lang = translate_response_local(session_start_time, target_tool=reader_id)
                        if not translated and terminal_screen_buffer:
                            # Fallback to terminal screen buffer
                            full_term_text = "".join(terminal_screen_buffer)
                            clean_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', full_term_text).strip()
                            term_lines = [l for l in clean_text.splitlines() if l.strip()]
                            if term_lines:
                                recent_block = "\n".join(term_lines[-40:]).strip()
                                if recent_block:
                                    translated = translate_prompt_local(recent_block, mode="response")
                                    target_lang = cfg.get("languages", {}).get("target_response", "uk")

                        if not translated:
                            os.write(sys.stdout.fileno(), f"\033[33m[{display_tag}]: No responses from {app_name} found in session logs yet.\033[0m\r\n".encode("utf-8"))
                            continue

                        # Store in variable to prevent accidental circular paste
                        last_copied_response = translated.strip()

                        try:
                            from .config import load_config
                            runtime_cfg = load_config()
                            copy_clip = runtime_cfg.get("copy_to_clipboard", False)
                        except Exception:
                            copy_clip = cfg.get("copy_to_clipboard", False)

                        # Copy to clipboard if enabled and on macOS
                        if copy_clip and sys.platform == "darwin":
                            try:
                                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                                p.communicate(translated.encode("utf-8"))
                            except Exception:
                                pass

                        from .renderer import str_display_width, render_markdown

                        term_cols = max(40, shutil.get_terminal_size((80, 24)).columns)
                        box_w = min(term_cols - 2, 80)
                        inner_w = box_w - 4
                        title = f"🐦 [{display_tag}] {app_name} Response ({target_lang.upper()})"
                        title_padded = title + " " * max(0, inner_w - str_display_width(title))
                        top_b = "╔" + "═" * (box_w - 2) + "╗"
                        mid_b = f"║ {title_padded} ║"
                        bot_b = "╚" + "═" * (box_w - 2) + "╝"
                        # Top Blue, Bottom Yellow styling
                        header = f"\r\n\033[38;5;39m\033[1m{top_b}\r\n{mid_b}\r\n\033[38;5;220m{bot_b}\033[0m\r\n\r\n"
                        os.write(sys.stdout.fileno(), header.encode("utf-8"))

                        rendered_body = render_markdown(translated, is_raw_term=True) + "\r\n"
                        os.write(sys.stdout.fileno(), rendered_body.encode("utf-8"))

                        clip_note = "📋 Copied to clipboard | " if copy_clip else ""
                        footer_div = "─" * min(term_cols - 2, 78)
                        footer = f"\r\n\033[38;5;220m\033[1m{footer_div}\033[0m\r\n" \
                                 f"\033[90m{clip_note}Continue working in {app_name}\033[0m\r\n"
                        os.write(sys.stdout.fileno(), footer.encode("utf-8"))
                    except Exception as e:
                        os.write(sys.stdout.fileno(), f"\r\n\033[31m[Response translation error: {e}]\033[0m\r\n".encode("utf-8"))
                    continue

                # 4. Clipboard Translation Hotkey (Ctrl+Y)
                if byte_clip in chunk:
                    clip_text = get_clipboard_text().strip()
                    if not clip_text:
                        os.write(sys.stdout.fileno(), f"\r\n\033[33m[{display_tag}]: Clipboard is empty.\033[0m\r\n".encode("utf-8"))
                        continue

                    # Safety guard: prevent dumping the translated agent response back into the prompt
                    if last_copied_response and clip_text == last_copied_response:
                        os.write(sys.stdout.fileno(), (
                            f"\r\n\033[33m⚠️  [{display_tag}]: Clipboard contains the previous translated response from {app_name}, not a prompt.\033[0m\r\n"
                            "\033[90mCopy your intended task (from browser or chat) and try again.\033[0m\r\n"
                        ).encode("utf-8"))
                        continue

                    lines_count = len(clip_text.splitlines())
                    if lines_count > 6 or len(clip_text) > 1200:
                        os.write(sys.stdout.fileno(), (
                            f"\r\n\033[33m⚠️  [{display_tag} Clipboard]: Text contains {lines_count} lines ({len(clip_text)} chars).\033[0m\r\n"
                            f"\033[1;36mSend as prompt? [y/N]: \033[0m"
                        ).encode("utf-8"))
                        confirm_ans = read_translation_line().strip().lower()
                        if confirm_ans not in ("y", "yes"):
                            os.write(sys.stdout.fileno(), "\033[90m(cancelled)\033[0m\r\n".encode("utf-8"))
                            continue

                    t_name, m_name = get_translator_info()
                    prompt_lang = cfg.get("languages", {}).get("target_prompt", "en")
                    try:
                        from .translator.base import get_language_name
                        prompt_lang_name = get_language_name(prompt_lang)
                    except Exception:
                        prompt_lang_name = prompt_lang.upper()
                    preview = (clip_text[:50] + "...") if len(clip_text) > 50 else clip_text
                    preview_single = preview.replace("\r", " ").replace("\n", " ")
                    os.write(sys.stdout.fileno(), f"\r\n\033[1;36m🐦 [{display_tag} Clipboard]:\033[0m \033[90m\"{preview_single}\"\033[0m\r\n".encode("utf-8"))
                    os.write(sys.stdout.fileno(), f"\033[90m[{t_name}: {m_name}] translating clipboard to {prompt_lang_name} ({prompt_lang.upper()})...\033[0m\r".encode("utf-8"))

                    try:
                        translated = translate_prompt_local(clip_text, mode="prompt")
                        os.write(sys.stdout.fileno(), b"\033[2K\r")
                        marker = f"\033[1;32m⚡ [{display_tag} Clipboard -> {prompt_lang.upper()}]:\033[0m {translated}\r\n".encode("utf-8")
                        os.write(sys.stdout.fileno(), marker)

                        # Bracketed paste mode so multi-line text doesn't cause rapid Enter presses
                        if "\n" in translated:
                            paste_payload = f"\033[200~{translated}\033[201~\r"
                        else:
                            paste_payload = f"{translated}\r"
                        os.write(master_fd, paste_payload.encode("utf-8"))
                    except Exception as e:
                        os.write(sys.stdout.fileno(), f"\r\n\033[31m[Clipboard translation error: {e}]\033[0m\r\n".encode("utf-8"))
                    continue

                # Normal 100% transparent passthrough (all keys, '/', Tab, arrows, ANSI reports)
                os.write(master_fd, chunk)

    finally:
        restore_terminal()
        try:
            os.close(master_fd)
        except Exception:
            pass

        try:
            _, exit_status = os.waitpid(pid, 0)
            sys.exit(os.waitstatus_to_exitcode(exit_status) if hasattr(os, "waitstatus_to_exitcode") else (exit_status >> 8))
        except Exception:
            sys.exit(0)

if __name__ == "__main__":
    main()
