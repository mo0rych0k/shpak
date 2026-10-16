import os
import sys
import shutil
import subprocess
from pathlib import Path
from .config import (
    load_config,
    save_config,
    get_prompt_template,
    detect_installed_agents,
    ensure_onboarding,
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_FORMATTED_PROMPT_TEMPLATE,
    DEFAULT_RESPONSE_TEMPLATE
)
from .translator.factory import create_translator
from .translator.base import get_language_name

BLUE_LINE = "\033[38;5;39m\033[1m"
YELLOW_LINE = "\033[38;5;220m\033[1m"
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"

def cmd_status():
    cfg = ensure_onboarding(load_config())
    active = cfg.get("active_translator", {})
    provider = active.get("provider", "agy-cli")
    model = active.get("model", "auto")
    prov_info = cfg.get("providers", {}).get(provider, {})
    prov_desc = prov_info.get("description", "CLI subscription")

    lang_cfg = cfg.get("languages", {})
    target_resp = lang_cfg.get("target_response", "uk")
    target_prompt = lang_cfg.get("target_prompt", "en")

    hotkeys = cfg.get("hotkeys", {})
    hk_p = hotkeys.get("translate_prompt", "ctrl+t").upper()
    hk_f = hotkeys.get("translate_prompt_formatted", "ctrl+f").upper()
    hk_r = hotkeys.get("translate_response", "ctrl+r").upper()
    hk_c = hotkeys.get("translate_clipboard", "ctrl+y").upper()

    print(f"{BLUE_LINE}═══════════════════════════════════════════════════════{RESET}")
    print("               🐦 Shpak CLI Status & Config            ")
    print(f"{BLUE_LINE}───────────────────────────────────────────────────────{RESET}")
    print(f"Active Backend      : {provider}")
    print(f"Model Selection     : {model}")
    print(f"Prompt Language     : {target_prompt.upper()} (User input -> English)")
    print(f"Response Language   : {target_resp.upper()} ({get_language_name(target_resp)})")
    print(f"Wrapper Hotkeys     : Prompt: {hk_p} | Markdown: {hk_f} | Response: {hk_r} | Clipboard: {hk_c}")
    print(f"Prompt Templates    : 1 Direct, 1 Formatted (Markdown), 1 Response")
    print(f"Backend Description : {prov_desc}")
    print("───────────────────────────────────────────────────────")
    print("Detected AI Coding Assistants:")
    agents = detect_installed_agents()
    for key, info in agents.items():
        if info["installed"]:
            status = f"{GREEN}✔ INSTALLED{RESET} ({info['path']})"
        else:
            status = f"{RED}✖ Not found in PATH{RESET}"
        print(f"  • {info['name']:<19} [{info['shpak_cmd']:<10}] : {status}")
    print("───────────────────────────────────────────────────────")
    print("Available CLI Providers (Zero API keys needed!):")
    for name, details in cfg.get("providers", {}).items():
        is_active = f" {GREEN}(ACTIVE){RESET}" if name == provider else ""
        print(f"  • {name:<12}{is_active} : {details.get('description', '')}")
    print(f"{YELLOW_LINE}═══════════════════════════════════════════════════════{RESET}")

def cmd_hotkeys(args: list = None):
    cfg = load_config()
    args = args or []

    if "--reset" in args:
        cfg["hotkeys"] = {
            "translate_prompt": "ctrl+t",
            "translate_prompt_formatted": "ctrl+f",
            "translate_response": "ctrl+r",
            "translate_clipboard": "ctrl+y"
        }
        save_config(cfg)
        print("✅ Hotkeys reset to defaults: Prompt=Ctrl+T, Markdown=Ctrl+F, Response=Ctrl+R, Clipboard=Ctrl+Y")
        return

    updated = False
    i = 0
    while i < len(args):
        if args[i] in ("--prompt", "-p") and i + 1 < len(args):
            cfg.setdefault("hotkeys", {})["translate_prompt"] = args[i + 1].lower()
            updated = True
            i += 2
        elif args[i] in ("--formatted", "--markdown", "-f") and i + 1 < len(args):
            cfg.setdefault("hotkeys", {})["translate_prompt_formatted"] = args[i + 1].lower()
            updated = True
            i += 2
        elif args[i] in ("--response", "-r") and i + 1 < len(args):
            cfg.setdefault("hotkeys", {})["translate_response"] = args[i + 1].lower()
            updated = True
            i += 2
        elif args[i] in ("--clipboard", "-c") and i + 1 < len(args):
            cfg.setdefault("hotkeys", {})["translate_clipboard"] = args[i + 1].lower()
            updated = True
            i += 2
        else:
            i += 1

    if updated:
        save_config(cfg)
        hk = cfg.get("hotkeys", {})
        print("✅ Hotkeys updated:")
        print(f"   Direct Prompt    : {hk.get('translate_prompt', 'ctrl+t').upper()}")
        print(f"   Formatted Prompt : {hk.get('translate_prompt_formatted', 'ctrl+f').upper()}")
        print(f"   Agent Response   : {hk.get('translate_response', 'ctrl+r').upper()}")
        print(f"   Clipboard        : {hk.get('translate_clipboard', 'ctrl+y').upper()}")
        return

    hk = cfg.get("hotkeys", {})
    print("═══════════════════════════════════════════════════════")
    print("              ⌨️  Wrapper Hotkey Bindings             ")
    print("═══════════════════════════════════════════════════════")
    print(f"  Direct Prompt (EN)      : {hk.get('translate_prompt', 'ctrl+t').upper()}")
    print(f"  Formatted Markdown (EN) : {hk.get('translate_prompt_formatted', 'ctrl+f').upper()}")
    print(f"  Response (UK)           : {hk.get('translate_response', 'ctrl+r').upper()}")
    print(f"  Clipboard (EN)          : {hk.get('translate_clipboard', 'ctrl+y').upper()}")
    print("───────────────────────────────────────────────────────")
    print("To change hotkeys:")
    print("  tr hotkeys --prompt ctrl+p")
    print("  tr hotkeys --formatted ctrl+g")
    print("  tr hotkeys --response ctrl+u")
    print("  tr hotkeys --clipboard ctrl+k")
    print("  tr hotkeys --reset")
    print("═══════════════════════════════════════════════════════")

def cmd_rules(args: list = None):
    cfg = load_config()
    args = args or []
    if "--formatted" in args or "--markdown" in args or "-f" in args:
        mode = "prompt_formatted"
    elif "--response" in args or "-r" in args:
        mode = "response"
    else:
        mode = "prompt"

    if "--reset" in args:
        if mode == "prompt_formatted":
            cfg.setdefault("prompts", {})["prompt_formatted"] = DEFAULT_FORMATTED_PROMPT_TEMPLATE
        elif mode == "prompt":
            cfg.setdefault("prompts", {})["prompt"] = DEFAULT_PROMPT_TEMPLATE
        else:
            cfg.setdefault("prompts", {})["response"] = DEFAULT_RESPONSE_TEMPLATE
        save_config(cfg)
        print(f"✅ Reset {mode} template to default built-in rules.")
        return

    if "--edit" in args:
        current = get_prompt_template(cfg, mode=mode)
        tmp_path = Path(f"/tmp/llm_translate_{mode}.txt")
        tmp_path.write_text(current, encoding="utf-8")
        editor = os.environ.get("EDITOR", "nano")
        print(f"📝 Opening {mode} prompt template in {editor}...")
        subprocess.run([editor, str(tmp_path)])
        updated = tmp_path.read_text(encoding="utf-8").strip()
        if updated:
            cfg.setdefault("prompts", {})[mode] = updated
            save_config(cfg)
            print(f"✅ {mode} template updated!")
        return

    prompt_content = get_prompt_template(cfg, mode=mode)
    print("═══════════════════════════════════════════════════════")
    print(f"      📝 Active 1-Prompt Rules for Mode: [{mode.upper()}]      ")
    print("═══════════════════════════════════════════════════════")
    print(prompt_content)
    print("───────────────────────────────────────────────────────")
    print("Options:")
    print(f"  tr rules --{mode} --edit     : Edit this prompt in $EDITOR")
    print(f"  tr rules --{mode} --reset    : Reset this prompt to defaults")
    print("  tr rules --prompt           : View direct user prompt template")
    print("  tr rules --formatted        : View formatted Markdown prompt template")
    print("  tr rules --response         : View agent response template")
    print("═══════════════════════════════════════════════════════")

def cmd_config(provider: str = None, model: str = None, lang: str = None):
    cfg = load_config()
    updated = False

    if provider:
        if provider not in cfg.get("providers", {}):
            print(f"❌ Unknown provider '{provider}'. Available: {list(cfg.get('providers', {}).keys())}")
            return
        cfg["active_translator"]["provider"] = provider
        if not model:
            cfg["active_translator"]["model"] = cfg["providers"][provider].get("default_model", "auto")
        updated = True

    if model:
        cfg["active_translator"]["model"] = model
        updated = True

    if lang:
        cfg.setdefault("languages", {})["target_response"] = lang
        updated = True

    if updated:
        save_config(cfg)
        print("✅ Configuration updated successfully:")
        print(f"   Provider      : {cfg['active_translator']['provider']}")
        print(f"   Model         : {cfg['active_translator']['model']}")
        print(f"   Response Lang : {cfg['languages']['target_response']}")
    else:
        cmd_status()
        print("\nTo switch backend, model or language, run:")
        print("  tr config --provider agy-cli --model gemini-3.8-flash-low")
        print("  tr config --provider claude-cli --model haiku")
        print("  tr config --lang uk")

def cmd_prompt(text: str, raw: bool = False, mode: str = "prompt"):
    if not text.strip():
        if not raw:
            print("Usage: tr prompt 'your prompt' or tr format 'your prompt'")
        return

    cfg = load_config()
    target_prompt = cfg.get("languages", {}).get("target_prompt", "en")
    translator = create_translator(cfg)
    label = "formatted Markdown" if mode == "prompt_formatted" else "clean technical"
    if not raw:
        print(f"🔄 Translating to {label} English via {cfg.get('active_translator', {}).get('provider')}...")
    try:
        translated = translator.translate(text, source_lang="auto", target_lang=target_prompt, mode=mode)
        if raw:
            print(translated)
            return

        print("\nTranslated Prompt:")
        print("───────────────────────────────────────────────────────")
        print(translated)
        print("───────────────────────────────────────────────────────")

        if sys.platform == "darwin":
            try:
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                p.communicate(translated.encode("utf-8"))
                print("📋 Copied to clipboard! (Ready to Cmd+V into agent)")
            except Exception:
                pass
    except Exception as e:
        print(f"❌ Translation error: {e}", file=sys.stderr if raw else sys.stdout)

def cmd_agent_exec(agent: str, text: str):
    if not text.strip():
        print(f"Usage: tr {agent} 'your prompt in any language'")
        return
    cfg = load_config()
    target_prompt = cfg.get("languages", {}).get("target_prompt", "en")
    translator = create_translator(cfg)
    print(f"🔄 Translating prompt to {target_prompt.upper()}...")
    try:
        translated = translator.translate(text, source_lang="auto", target_lang=target_prompt, mode="prompt")
        print(f"🚀 Passing translated prompt to {agent}:")
        print(f"   \"{translated}\"\n")
        subprocess.run([agent, translated])
    except Exception as e:
        print(f"❌ Error: {e}")

def cmd_clip():
    try:
        if sys.platform == "darwin":
            raw = subprocess.check_output(["pbpaste"]).decode("utf-8").strip()
        else:
            raw = subprocess.check_output(["xclip", "-selection", "clipboard", "-o"]).decode("utf-8").strip()

        if not raw:
            print("Clipboard is empty.")
            return

        cfg = load_config()
        target_resp = cfg.get("languages", {}).get("target_response", "uk")
        print(f"📋 Translating clipboard content to {target_resp.upper()}...")
        translator = create_translator(cfg)
        translated = translator.translate(raw, source_lang="auto", target_lang=target_resp, mode="response")
        print("\nTranslated:")
        print("───────────────────────────────────────────────────────")
        print(translated)
        print("───────────────────────────────────────────────────────")
    except Exception as e:
        print(f"❌ Error: {e}")

def cmd_last():
    from .reader import get_latest_agent_response
    from .renderer import render_markdown
    cfg = load_config()
    target_resp = cfg.get("languages", {}).get("target_response", "uk")
    translator = create_translator(cfg)
    
    print("🔄 Fetching latest agent response...")
    raw_text = get_latest_agent_response()
    if not raw_text:
        print("❌ No agent response found in session logs.")
        return

    active = cfg.get("active_translator", {})
    t_name = "agy" if "agy" in active.get("provider", "") else ("claude" if "claude" in active.get("provider", "") else active.get("provider", "agy"))
    m_name = active.get("model", "gemini-3.8-flash-low")
    print(f"🔄 [{t_name}: {m_name}] translating response to {target_resp.upper()}...")
    try:
        translated = translator.translate(raw_text, source_lang="auto", target_lang=target_resp, mode="response")
        if sys.platform == "darwin":
            try:
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                p.communicate(translated.encode("utf-8"))
            except Exception:
                pass

        print(f"\n{BLUE_LINE}═══════════════════════════════════════════════════════{RESET}")
        print(f"         🌐 Translated Agent Response ({target_resp.upper()})")
        print(f"{BLUE_LINE}───────────────────────────────────────────────────────{RESET}\n")
        print(render_markdown(translated, is_raw_term=False))
        print(f"\n{YELLOW_LINE}───────────────────────────────────────────────────────{RESET}")
        print("📋 Copied to clipboard!")
        print(f"{YELLOW_LINE}═══════════════════════════════════════════════════════{RESET}")
    except Exception as e:
        print(f"❌ Translation error: {e}")

def cmd_agents():
    """Displays installed and supported AI coding assistants."""
    agents = detect_installed_agents()
    print(f"\n{BLUE_LINE}═══════════════════════════════════════════════════════{RESET}")
    print("           🤖 Supported AI Coding Assistants           ")
    print(f"{BLUE_LINE}───────────────────────────────────────────────────────{RESET}")
    for key, info in agents.items():
        if info["installed"]:
            status = f"{GREEN}✔ INSTALLED{RESET} ({info['path']})"
        else:
            status = f"{RED}✖ Not found in PATH{RESET}"
        print(f"  • {info['name']:<19} [{info['shpak_cmd']:<10}] : {status}")
    print(f"{YELLOW_LINE}═══════════════════════════════════════════════════════{RESET}\n")

def cmd_install():
    """Symlinks binaries into ~/.local/bin and verifies PATH."""
    repo_dir = Path(__file__).resolve().parent.parent
    install_script = repo_dir / "install.sh"
    if install_script.exists():
        subprocess.run(["bash", str(install_script)])
    else:
        curl_cmd = "curl -fsSL https://raw.githubusercontent.com/mo0rych0k/shpak/main/install.sh | bash"
        subprocess.run(curl_cmd, shell=True)

def cmd_update():
    """Pulls latest updates and refreshes symlinks."""
    repo_dir = Path(__file__).resolve().parent.parent
    git_dir = repo_dir / ".git"
    if git_dir.exists():
        print("🔄 Updating Shpak via Git...")
        res = subprocess.run(["git", "-C", str(repo_dir), "pull"])
        if res.returncode == 0:
            install_script = repo_dir / "install.sh"
            if install_script.exists():
                subprocess.run(["bash", str(install_script)])
            print("✅ Shpak updated successfully!")
        else:
            print("❌ Error executing git pull.")
    else:
        shpak_home = Path.home() / ".shpak"
        if (shpak_home / ".git").exists():
            print("🔄 Updating Shpak in ~/.shpak...")
            subprocess.run(["git", "-C", str(shpak_home), "pull"])
            subprocess.run(["bash", str(shpak_home / "install.sh")])
            print("✅ Shpak updated successfully!")
        else:
            print("🔄 Downloading and updating latest Shpak release...")
            curl_cmd = "curl -fsSL https://raw.githubusercontent.com/mo0rych0k/shpak/main/install.sh | bash"
            subprocess.run(curl_cmd, shell=True)

def main():
    args = sys.argv[1:]
    cfg = ensure_onboarding(load_config())

    if not args:
        from .tui import run_tui
        run_tui()
        return

    if args[0] in ("-h", "--help", "help"):
        print("""Usage: spk [command] [options]  (alias: shpak)

Commands:
  (default)             Launch interactive Terminal UI (TUI)
  tui                   Launch interactive Terminal UI (TUI)
  status                Show active provider, model, hotkeys, and agent status
  agents                List detected and supported AI coding assistants
  install               Install / refresh CLI symlinks into ~/.local/bin
  update                Pull latest updates and reinstall Shpak
  hotkeys [options]     View or change wrapper hotkeys (Ctrl+T, Ctrl+F, Ctrl+R, Ctrl+Y):
      --prompt <key>    Change direct prompt hotkey (e.g. ctrl+p)
      --formatted <key> Change formatted Markdown hotkey (e.g. ctrl+g)
      --response <key>  Change response hotkey (e.g. ctrl+u)
      --clipboard <key> Change clipboard hotkey (e.g. ctrl+k)
      --reset           Reset hotkeys to defaults
  rules [options]       View and customize prompt templates:
      --prompt          View direct user prompt template (Prompt -> EN)
      --formatted       View structured Markdown prompt template
      --response        View agent response template (Response -> UK)
      --edit            Edit active template in $EDITOR
      --reset           Reset active template to defaults
  config [options]      View or change active translation provider:
      --provider <name> (agy-cli, claude-cli)
      --model <name>    (e.g. auto, gemini-3.8-flash-low, haiku)
      --lang <code>     (e.g. uk, pl, de, es, fr)
  prompt "<text>"       Translate prompt directly to English and copy to clipboard
  format "<text>"       Translate and format prompt into structured Markdown
  raw "<text>"          Output ONLY the clean translated English string
  last                  Translate the latest response from Antigravity session
  clip                  Translate current clipboard content
  demo                  Launch interactive zero-account test sandbox
  agy "<prompt>"        Translate prompt to English and run 'agy "<prompt>"'
  claude "<prompt>"     Translate prompt to English and run 'claude "<prompt>"'
""")
        return

    cmd = args[0]
    if cmd in ("tui", "menu"):
        from .tui import run_tui
        run_tui()
    elif cmd == "status":
        cmd_status()
    elif cmd in ("agents", "list", "check"):
        cmd_agents()
    elif cmd in ("install", "setup"):
        cmd_install()
    elif cmd in ("update", "upgrade"):
        cmd_update()
    elif cmd in ("hotkeys", "hotkey", "keys"):
        cmd_hotkeys(args[1:])
    elif cmd in ("format", "md", "structure"):
        clean_args = [a for a in args[1:] if a != "--raw"]
        cmd_prompt(" ".join(clean_args), raw="--raw" in args, mode="prompt_formatted")
    elif cmd in ("rules", "prompt-rules", "prompts"):
        cmd_rules(args[1:])
    elif cmd in ("last", "reply", "response"):
        cmd_last()
    elif cmd == "raw":
        cmd_prompt(" ".join(args[1:]), raw=True, mode="prompt")
    elif cmd == "clip":
        cmd_clip()
    elif cmd in ("agy", "claude", "codex", "cursor"):
        wrapper_path = Path(__file__).parent.parent / "agy-shpak"
        if not wrapper_path.exists():
            wrapper_path = Path(shutil.which("agy-shpak") or shutil.which("ag-tr") or "agy-shpak")
        subprocess.run([sys.executable, str(wrapper_path), f"--target={cmd}"] + args[1:])
    elif cmd in ("demo", "test"):
        wrapper_path = Path(__file__).parent.parent / "agy-shpak"
        if not wrapper_path.exists():
            wrapper_path = Path(shutil.which("agy-shpak") or shutil.which("ag-tr") or "agy-shpak")
        subprocess.run([sys.executable, str(wrapper_path), "--demo"])
    elif cmd == "config":
        provider = None
        model = None
        lang = None
        i = 1
        while i < len(args):
            if args[i] == "--provider" and i + 1 < len(args):
                provider = args[i + 1]
                i += 2
            elif args[i] == "--model" and i + 1 < len(args):
                model = args[i + 1]
                i += 2
            elif args[i] in ("--lang", "--language") and i + 1 < len(args):
                lang = args[i + 1]
                i += 2
            else:
                i += 1
        cmd_config(provider=provider, model=model, lang=lang)
    elif cmd in ("prompt", "p"):
        raw = "--raw" in args
        clean_args = [a for a in args[1:] if a != "--raw"]
        cmd_prompt(" ".join(clean_args), raw=raw, mode="prompt")
    else:
        cmd_prompt(" ".join(args), mode="prompt")

if __name__ == "__main__":
    main()
