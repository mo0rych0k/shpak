import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from .config import (
    load_config,
    save_config,
    detect_installed_agents,
    print_spk_logo,
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_FORMATTED_PROMPT_TEMPLATE,
    DEFAULT_RESPONSE_TEMPLATE
)
from .translator.factory import create_translator
from .translator.base import get_language_name

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RED = "\033[31m"
WHITE = "\033[97m"
GRAY = "\033[90m"
BLUE_LINE = "\033[38;5;39m\033[1m"
YELLOW_LINE = "\033[38;5;220m\033[1m"

def clear_screen():
    print("\033[2J\033[H", end="")

def print_header(cfg: dict):
    clear_screen()
    print_spk_logo()
    print()
    active = cfg.get("active_translator", {})
    provider = active.get("provider", "agy-cli")
    model = active.get("model", "auto")
    lang_cfg = cfg.get("languages", {})
    target_resp = lang_cfg.get("target_response", "uk")
    target_prompt = lang_cfg.get("target_prompt", "en")
    hotkeys = cfg.get("hotkeys", {})
    hk_p = hotkeys.get("translate_prompt", "ctrl+t").upper()
    hk_f = hotkeys.get("translate_prompt_formatted", "ctrl+f").upper()
    hk_r = hotkeys.get("translate_response", "ctrl+r").upper()
    hk_c = hotkeys.get("translate_clipboard", "ctrl+y").upper()

    copy_clip = cfg.get("copy_to_clipboard", False)
    clip_status = f"{GREEN}ON{RESET}" if copy_clip else f"{RED}OFF{RESET}"

    print(f"  Backend   : {BOLD}{YELLOW}{provider}{RESET}  |  Model: {BOLD}{CYAN}{model}{RESET}  |  Auto-Copy: {BOLD}{clip_status}{RESET}")
    print(f"  Languages : Response: {BOLD}{GREEN}{target_resp.upper()} ({get_language_name(target_resp)}){RESET}  |  Prompt: {BOLD}{CYAN}{target_prompt.upper()} ({get_language_name(target_prompt)}){RESET}")
    print(f"  Hotkeys   : {BOLD}{WHITE}Prompt: {hk_p}  |  Markdown: {hk_f}  |  Response: {hk_r}  |  Clipboard: {hk_c}{RESET}")
    print(f"{YELLOW_LINE}─────────────────────────────────────────────────────────────────────────────{RESET}")

def menu_select_provider(cfg: dict):
    clear_screen()
    print(f"{CYAN}{BOLD}=== 🤖 SELECT TRANSLATION CLI PROVIDER ==={RESET}\n")
    providers = cfg.get("providers", {})
    keys = list(providers.keys())

    for idx, key in enumerate(keys, 1):
        info = providers[key]
        desc = info.get("description", "")
        current = f" {GREEN}(CURRENT){RESET}" if key == cfg["active_translator"]["provider"] else ""
        print(f"  [{BOLD}{idx}{RESET}] {YELLOW}{key:<12}{RESET} - {desc}{current}")

    print(f"\n  [{BOLD}0{RESET}] Back to Main Menu")

    choice = input(f"\n{BOLD}Select provider [1-{len(keys)}]: {RESET}").strip()
    if choice in ("0", "q", "exit"):
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(keys):
            selected = keys[idx]
            cfg["active_translator"]["provider"] = selected
            cfg["active_translator"]["model"] = providers[selected].get("default_model", "auto")
            save_config(cfg)
            print(f"\n{GREEN}✅ Provider changed to '{selected}' (model: {cfg['active_translator']['model']}){RESET}")
            time.sleep(1)
    except ValueError:
        pass

def menu_select_model(cfg: dict):
    clear_screen()
    provider = cfg["active_translator"]["provider"]
    current_model = cfg["active_translator"]["model"]
    prov_cfg = cfg.get("providers", {}).get(provider, {})
    models = prov_cfg.get("models", [])

    print(f"{CYAN}{BOLD}=== 🧠 SELECT MODEL FOR {provider.upper()} ==={RESET}\n")
    if not models:
        print("  No predefined models for this provider.")
    else:
        for idx, m in enumerate(models, 1):
            current = f" {GREEN}(CURRENT){RESET}" if m == current_model else ""
            print(f"  [{BOLD}{idx}{RESET}] {m}{current}")

    print(f"\n  [{BOLD}C{RESET}] Custom model name")
    print(f"  [{BOLD}0{RESET}] Back to Main Menu")

    choice = input(f"\n{BOLD}Select option: {RESET}").strip()
    if choice in ("0", "q", "exit"):
        return

    if choice.upper() == "C":
        custom = input(f"{BOLD}Enter custom model ID: {RESET}").strip()
        if custom:
            cfg["active_translator"]["model"] = custom
            save_config(cfg)
            print(f"\n{GREEN}✅ Model set to '{custom}'{RESET}")
            time.sleep(1)
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(models):
            cfg["active_translator"]["model"] = models[idx]
            save_config(cfg)
            print(f"\n{GREEN}✅ Model changed to '{models[idx]}'{RESET}")
            time.sleep(1)
    except ValueError:
        pass

def choose_single_language(title: str, current_code: str) -> str:
    clear_screen()
    print(f"{CYAN}{BOLD}=== 🌍 {title} ==={RESET}\n")
    popular = [
        ("uk", "Ukrainian"),
        ("en", "English"),
        ("pl", "Polish"),
        ("de", "German"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("it", "Italian"),
        ("ja", "Japanese"),
        ("zh", "Chinese"),
        ("pt", "Portuguese"),
    ]

    for idx, (code, name) in enumerate(popular, 1):
        is_cur = f" {GREEN}(CURRENT){RESET}" if code == current_code else ""
        print(f"  [{BOLD}{idx}{RESET}] {code.upper():<4} - {name}{is_cur}")

    print(f"\n  [{BOLD}C{RESET}] Enter another custom language code (e.g. nl, tr, cs, sv, ko)")
    print(f"  [{BOLD}0{RESET}] Keep Current ({current_code.upper()})")

    choice = input(f"\n{BOLD}Select language: {RESET}").strip()
    if choice in ("0", "q", "exit", ""):
        return current_code

    if choice.upper() == "C":
        custom = input(f"{BOLD}Enter 2-letter ISO language code: {RESET}").strip().lower()
        return custom if custom else current_code

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(popular):
            return popular[idx][0]
    except ValueError:
        if len(choice) <= 4:
            return choice.lower()
    return current_code

def menu_select_language(cfg: dict):
    while True:
        clear_screen()
        lang_cfg = cfg.setdefault("languages", {})
        resp_lang = lang_cfg.get("target_response", "uk")
        prompt_lang = lang_cfg.get("target_prompt", "en")

        print(f"{CYAN}{BOLD}=== 🌍 CONFIGURE TRANSLATION LANGUAGES ==={RESET}\n")
        print(f"  Current Settings:")
        print(f"    • Agent Response (Agent -> You)   : {BOLD}{GREEN}{resp_lang.upper()} ({get_language_name(resp_lang)}){RESET}")
        print(f"    • Developer Prompt (You -> Agent) : {BOLD}{CYAN}{prompt_lang.upper()} ({get_language_name(prompt_lang)}){RESET}\n")
        print(f"  [{BOLD}1{RESET}] 🔄 Change Agent Response Language (Agent -> You)")
        print(f"  [{BOLD}2{RESET}] 🔄 Change Developer Prompt Language (You -> Agent)")
        print(f"  [{BOLD}3{RESET}] 🔀 Swap Languages ({prompt_lang.upper()} <-> {resp_lang.upper()})")
        print(f"\n  [{BOLD}0{RESET}] Back to Main Menu")

        choice = input(f"\n{BOLD}Select option: {RESET}").strip()
        if choice in ("0", "q", "exit"):
            break
        elif choice == "1":
            new_code = choose_single_language("SELECT AGENT RESPONSE LANGUAGE (Agent -> You)", resp_lang)
            if new_code != resp_lang:
                cfg["languages"]["target_response"] = new_code
                save_config(cfg)
                print(f"\n{GREEN}✅ Response language set to '{new_code.upper()}' ({get_language_name(new_code)}){RESET}")
                time.sleep(1)
        elif choice == "2":
            new_code = choose_single_language("SELECT DEVELOPER PROMPT LANGUAGE (You -> Agent)", prompt_lang)
            if new_code != prompt_lang:
                cfg["languages"]["target_prompt"] = new_code
                save_config(cfg)
                print(f"\n{GREEN}✅ Prompt language set to '{new_code.upper()}' ({get_language_name(new_code)}){RESET}")
                time.sleep(1)
        elif choice == "3":
            cfg["languages"]["target_response"], cfg["languages"]["target_prompt"] = prompt_lang, resp_lang
            save_config(cfg)
            print(f"\n{GREEN}✅ Swapped languages! Response is now {prompt_lang.upper()}, Prompt is {resp_lang.upper()}.{RESET}")
            time.sleep(1.2)

def menu_hotkeys(cfg: dict):
    while True:
        clear_screen()
        hotkeys = cfg.get("hotkeys", {})
        hk_p = hotkeys.get("translate_prompt", "ctrl+t").upper()
        hk_f = hotkeys.get("translate_prompt_formatted", "ctrl+f").upper()
        hk_r = hotkeys.get("translate_response", "ctrl+r").upper()
        hk_c = hotkeys.get("translate_clipboard", "ctrl+y").upper()

        print(f"{CYAN}{BOLD}=== ⌨️  CONFIGURE TERMINAL WRAPPER HOTKEYS ==={RESET}\n")
        print(f"  [{BOLD}1{RESET}] Direct Prompt Translation Hotkey    : {BOLD}{GREEN}{hk_p}{RESET}")
        print(f"  [{BOLD}2{RESET}] Formatted Markdown Prompt Hotkey    : {BOLD}{MAGENTA}{hk_f}{RESET}")
        print(f"  [{BOLD}3{RESET}] Agent Response Translation Hotkey   : {BOLD}{GREEN}{hk_r}{RESET}")
        print(f"  [{BOLD}4{RESET}] Clipboard Translation Hotkey        : {BOLD}{GREEN}{hk_c}{RESET}")
        print(f"  [{BOLD}5{RESET}] 🔄 Reset Hotkeys to Defaults (Ctrl+T, Ctrl+F, Ctrl+R, Ctrl+Y)")
        print(f"\n  [{BOLD}0{RESET}] Back to Main Menu")

        choice = input(f"\n{BOLD}Select option: {RESET}").strip()
        if choice in ("0", "q", "exit"):
            break
        elif choice == "1":
            val = input(f"{BOLD}Enter new hotkey for direct prompt (e.g. ctrl+t, ctrl+p): {RESET}").strip().lower()
            if val:
                cfg.setdefault("hotkeys", {})["translate_prompt"] = val
                save_config(cfg)
                print(f"\n{GREEN}✅ Direct prompt hotkey set to {val.upper()}{RESET}")
                time.sleep(1)
        elif choice == "2":
            val = input(f"{BOLD}Enter new hotkey for Markdown formatted prompt (e.g. ctrl+f, ctrl+g): {RESET}").strip().lower()
            if val:
                cfg.setdefault("hotkeys", {})["translate_prompt_formatted"] = val
                save_config(cfg)
                print(f"\n{GREEN}✅ Formatted prompt hotkey set to {val.upper()}{RESET}")
                time.sleep(1)
        elif choice == "3":
            val = input(f"{BOLD}Enter new hotkey for response (e.g. ctrl+r, ctrl+u): {RESET}").strip().lower()
            if val:
                cfg.setdefault("hotkeys", {})["translate_response"] = val
                save_config(cfg)
                print(f"\n{GREEN}✅ Response hotkey set to {val.upper()}{RESET}")
                time.sleep(1)
        elif choice == "4":
            val = input(f"{BOLD}Enter new hotkey for clipboard (e.g. ctrl+y, ctrl+k): {RESET}").strip().lower()
            if val:
                cfg.setdefault("hotkeys", {})["translate_clipboard"] = val
                save_config(cfg)
                print(f"\n{GREEN}✅ Clipboard hotkey set to {val.upper()}{RESET}")
                time.sleep(1)
        elif choice == "5":
            cfg["hotkeys"] = {
                "translate_prompt": "ctrl+t",
                "translate_prompt_formatted": "ctrl+f",
                "translate_response": "ctrl+r",
                "translate_clipboard": "ctrl+y"
            }
            save_config(cfg)
            print(f"\n{GREEN}✅ Hotkeys reset to defaults.{RESET}")
            time.sleep(1)

def menu_prompts(cfg: dict):
    while True:
        clear_screen()
        print(f"{CYAN}{BOLD}=== 📝 TRANSLATION PROMPTS (1 SELF-CONTAINED PROMPT PER VARIANT) ==={RESET}\n")
        print(f"  [{BOLD}1{RESET}] 👁️  Preview Direct Prompt Template (Prompt -> English)")
        print(f"  [{BOLD}2{RESET}] 👁️  Preview Formatted Markdown Prompt Template (Prompt -> Structured Markdown)")
        print(f"  [{BOLD}3{RESET}] 👁️  Preview Agent Response Template (Response -> Ukrainian, Zero Omissions)")
        print(f"  [{BOLD}4{RESET}] ✏️  Edit Direct Prompt Template in $EDITOR")
        print(f"  [{BOLD}5{RESET}] ✏️  Edit Formatted Markdown Prompt Template in $EDITOR")
        print(f"  [{BOLD}6{RESET}] ✏️  Edit Agent Response Template in $EDITOR")
        print(f"  [{BOLD}7{RESET}] 🔄 Reset All Prompts to Defaults")
        print(f"\n  [{BOLD}0{RESET}] Back to Main Menu")

        choice = input(f"\n{BOLD}Select option: {RESET}").strip()
        if choice in ("0", "q", "exit"):
            break
        elif choice == "1":
            clear_screen()
            print(f"{CYAN}{BOLD}=== 📜 DIRECT USER PROMPT TEMPLATE (Prompt -> EN) ==={RESET}\n")
            print(cfg.get("prompts", {}).get("prompt", DEFAULT_PROMPT_TEMPLATE))
            print(f"\n{DIM}────────────────────────────────────────────────────────────{RESET}")
            input(f"{DIM}Press Enter to return...{RESET}")
        elif choice == "2":
            clear_screen()
            print(f"{MAGENTA}{BOLD}=== 📜 FORMATTED MARKDOWN PROMPT TEMPLATE (Prompt -> Markdown) ==={RESET}\n")
            print(cfg.get("prompts", {}).get("prompt_formatted", DEFAULT_FORMATTED_PROMPT_TEMPLATE))
            print(f"\n{DIM}────────────────────────────────────────────────────────────{RESET}")
            input(f"{DIM}Press Enter to return...{RESET}")
        elif choice == "3":
            clear_screen()
            print(f"{CYAN}{BOLD}=== 📜 AGENT RESPONSE TEMPLATE (Response -> UK) ==={RESET}\n")
            print(cfg.get("prompts", {}).get("response", DEFAULT_RESPONSE_TEMPLATE))
            print(f"\n{DIM}────────────────────────────────────────────────────────────{RESET}")
            input(f"{DIM}Press Enter to return...{RESET}")
        elif choice == "4":
            current = cfg.get("prompts", {}).get("prompt", DEFAULT_PROMPT_TEMPLATE)
            tmp_path = Path("/tmp/llm_translate_prompt.txt")
            tmp_path.write_text(current, encoding="utf-8")
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(tmp_path)])
            updated = tmp_path.read_text(encoding="utf-8").strip()
            if updated:
                cfg.setdefault("prompts", {})["prompt"] = updated
                save_config(cfg)
                print(f"\n{GREEN}✅ Direct prompt template updated!{RESET}")
                time.sleep(1)
        elif choice == "5":
            current = cfg.get("prompts", {}).get("prompt_formatted", DEFAULT_FORMATTED_PROMPT_TEMPLATE)
            tmp_path = Path("/tmp/llm_translate_prompt_formatted.txt")
            tmp_path.write_text(current, encoding="utf-8")
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(tmp_path)])
            updated = tmp_path.read_text(encoding="utf-8").strip()
            if updated:
                cfg.setdefault("prompts", {})["prompt_formatted"] = updated
                save_config(cfg)
                print(f"\n{GREEN}✅ Formatted Markdown prompt template updated!{RESET}")
                time.sleep(1)
        elif choice == "6":
            current = cfg.get("prompts", {}).get("response", DEFAULT_RESPONSE_TEMPLATE)
            tmp_path = Path("/tmp/llm_translate_response.txt")
            tmp_path.write_text(current, encoding="utf-8")
            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(tmp_path)])
            updated = tmp_path.read_text(encoding="utf-8").strip()
            if updated:
                cfg.setdefault("prompts", {})["response"] = updated
                save_config(cfg)
                print(f"\n{GREEN}✅ Agent response template updated!{RESET}")
                time.sleep(1)
        elif choice == "7":
            cfg.setdefault("prompts", {})["prompt"] = DEFAULT_PROMPT_TEMPLATE
            cfg.setdefault("prompts", {})["prompt_formatted"] = DEFAULT_FORMATTED_PROMPT_TEMPLATE
            cfg.setdefault("prompts", {})["response"] = DEFAULT_RESPONSE_TEMPLATE
            save_config(cfg)
            print(f"\n{GREEN}✅ All prompts reset to default rules.{RESET}")
            time.sleep(1)

def test_translation(cfg: dict):
    clear_screen()
    print(f"{CYAN}{BOLD}=== 🧪 TEST LIVE TRANSLATION ==={RESET}\n")
    provider = cfg["active_translator"]["provider"]
    model = cfg["active_translator"]["model"]
    target_prompt = cfg.get("languages", {}).get("target_prompt", "en")
    target_resp = cfg.get("languages", {}).get("target_response", "uk")

    print(f"Provider: {YELLOW}{provider}{RESET} ({model})\n")
    print(f"  [{BOLD}1{RESET}] Test Direct Prompt -> EN")
    print(f"  [{BOLD}2{RESET}] Test Formatted Markdown Prompt -> Markdown EN")
    print(f"  [{BOLD}3{RESET}] Test Response -> {target_resp.upper()}")
    print(f"  [{BOLD}0{RESET}] Back to Main Menu")

    mode_choice = input(f"\n{BOLD}Select test mode: {RESET}").strip()
    if mode_choice == "0":
        return
    elif mode_choice == "2":
        mode = "prompt_formatted"
        tgt = target_prompt
    elif mode_choice == "3":
        mode = "response"
        tgt = target_resp
    else:
        mode = "prompt"
        tgt = target_prompt

    text = input(f"\n{BOLD}Enter text to translate (or press Enter for default): {RESET}").strip()
    if not text:
        text = "create an asynchronous HTTP server in FastAPI and verify the response status code"

    print(f"\n🔄 Translating in mode [{mode}]...")
    translator = create_translator(cfg)
    try:
        start_t = time.time()
        translated = translator.translate(text, source_lang="auto", target_lang=tgt, mode=mode)
        elapsed = time.time() - start_t
        print(f"\n{GREEN}{BOLD}Result ({elapsed:.2f}s):{RESET}")
        print(f"────────────────────────────────────────────────────────────")
        print(f"{translated}")
        print(f"────────────────────────────────────────────────────────────")
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")

    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

def menu_launch_wrapper(cfg: dict) -> bool:
    clear_screen()
    agents = detect_installed_agents()
    print(f"{CYAN}{BOLD}=== 🚀 LAUNCH AI CODING CLI WITH TRANSLATION WRAPPER ==={RESET}\n")
    print(f"{BOLD}Detected AI Coding Assistants:{RESET}\n")

    tools = [
        ("1", "agy", "Antigravity", "agy-spk"),
        ("2", "claude", "Claude Code", "claude-spk"),
        ("3", "codex", "Codex CLI", "codex-spk"),
        ("4", "cursor", "Cursor Agent", "cursor-spk"),
        ("5", "aider", "Aider", "spk aider"),
    ]

    for key_idx, tool_id, name, shpak_cmd in tools:
        ag_info = agents.get(tool_id, {})
        if ag_info.get("installed", False):
            badge = f"{GREEN}✔ INSTALLED{RESET} {GRAY}({ag_info.get('path')}){RESET}"
        else:
            badge = f"{RED}✖ Not found in PATH{RESET}"
        test_badge = f"{GREEN}[TESTED STABLE]{RESET}" if tool_id == "agy" else f"{YELLOW}[EXPERIMENTAL]{RESET}"
        print(f"  [{BOLD}{key_idx}{RESET}] {name:<15} ({YELLOW}{shpak_cmd:<10}{RESET}) : {badge} {test_badge}")

    print(f"\n  {YELLOW}⚠️  Note: Shpak is actively verified on Antigravity. Other CLIs are experimental.{RESET}")
    print(f"  [{BOLD}6{RESET}] Universal CLI  ({YELLOW}spk run <cmd>{RESET}) : Wrap any terminal command")
    print(f"  [{BOLD}T{RESET}] Demo Sandbox  ({YELLOW}spk demo{RESET})      : Test hotkeys & features without accounts")
    print(f"\n  [{BOLD}0{RESET}] Back to Main Menu")

    choice = input(f"\n{BOLD}Select CLI to launch [1-6 / T]: {RESET}").strip()
    if choice in ("0", "q", "exit"):
        return False

    wrapper_path = Path(__file__).parent.parent / "agy-shpak"
    if not wrapper_path.exists():
        wrapper_path = Path(shutil.which("agy-shpak") or shutil.which("agy-spk") or "agy-shpak")

    cmd = [sys.executable, str(wrapper_path)]

    selected_tool = None
    if choice == "1":
        selected_tool = "agy"
        cmd.append("--target=agy")
    elif choice == "2":
        selected_tool = "claude"
        cmd.append("--target=claude")
    elif choice == "3":
        selected_tool = "codex"
        cmd.append("--target=codex")
    elif choice == "4":
        selected_tool = "cursor"
        cmd.append("--target=cursor")
    elif choice == "5":
        selected_tool = "aider"
        cmd.append("--target=aider")
    elif choice.upper() == "T":
        cmd.append("--demo")
    elif choice == "6":
        custom = input(f"\n{BOLD}Enter CLI command to wrap (e.g. aider, python3): {RESET}").strip()
        if not custom:
            return False
        cmd.extend(["--target", custom])
    else:
        return False

    if selected_tool:
        ag_info = agents.get(selected_tool, {})
        if not ag_info.get("installed", False):
            print(f"\n{YELLOW}⚠️  Note: '{ag_info.get('name')}' ({ag_info.get('cmd')}) was not found in your PATH.{RESET}")
            confirm = input(f"{BOLD}Try to launch anyway? [y/N]: {RESET}").strip().lower()
            if confirm not in ("y", "yes"):
                return False

    clear_screen()
    subprocess.run(cmd)
    return True

def run_tui():
    while True:
        cfg = load_config()
        print_header(cfg)

        copy_clip = cfg.get("copy_to_clipboard", False)
        clip_btn = f"{GREEN}ON{RESET}" if copy_clip else f"{RED}OFF{RESET}"
        lang_cfg = cfg.get("languages", {})
        r_code = lang_cfg.get("target_response", "uk").upper()
        p_code = lang_cfg.get("target_prompt", "en").upper()

        print(f"  [{BOLD}1{RESET}] 🤖 Switch Translation Provider {DIM}(agy-cli / claude-cli){RESET}")
        print(f"  [{BOLD}2{RESET}] 🧠 Switch Model {DIM}(gemini-3.8-flash-low, haiku, auto...){RESET}")
        print(f"  [{BOLD}3{RESET}] 🌍 Configure Languages {DIM}(Response: {r_code}, Prompt: {p_code}){RESET}")
        print(f"  [{BOLD}4{RESET}] ⌨️  Configure Hotkeys {DIM}(Ctrl+T, Ctrl+F, Ctrl+R, Ctrl+Y){RESET}")
        print(f"  [{BOLD}5{RESET}] 📝 View & Edit Prompts {DIM}(Direct, Markdown, Response){RESET}")
        print(f"  [{BOLD}6{RESET}] 📋 Auto-Copy Translation to Clipboard: [{clip_btn}]")
        print(f"  [{BOLD}7{RESET}] 🧪 Test Live Translation")
        print(f"  [{BOLD}8{RESET}] 🚀 Launch AI CLI Wrapper {DIM}(agy-spk, claude-spk, codex-spk...){RESET}")
        print(f"  [{BOLD}0{RESET}] Exit")

        choice = input(f"\n{BOLD}Option [0-8]: {RESET}").strip()

        if choice in ("0", "q", "exit"):
            clear_screen()
            break
        elif choice == "1":
            menu_select_provider(cfg)
        elif choice == "2":
            menu_select_model(cfg)
        elif choice == "3":
            menu_select_language(cfg)
        elif choice == "4":
            menu_hotkeys(cfg)
        elif choice == "5":
            menu_prompts(cfg)
        elif choice == "6":
            new_val = not copy_clip
            cfg["copy_to_clipboard"] = new_val
            save_config(cfg)
            status_text = "ENABLED" if new_val else "DISABLED"
            print(f"\n{GREEN}✅ Auto-copy to clipboard {status_text}!{RESET}")
            time.sleep(0.8)
        elif choice == "7":
            test_translation(cfg)
        elif choice == "8":
            if menu_launch_wrapper(cfg):
                break
