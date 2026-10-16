import subprocess
import shutil
from pathlib import Path
from .base import BaseTranslator, get_language_name

class CLITranslator(BaseTranslator):
    """Translates text by invoking local CLI agents (agy, claude, etc.) under the user's active subscription (NO API KEYS REQUIRED)."""

    def __init__(self, system_prompt: str = "", cli_tool: str = "agy", model: str = "", prompts: dict = None):
        super().__init__(system_prompt=system_prompt, model=model, base_url="", api_key="", prompts=prompts)
        self.cli_tool = cli_tool

    def _resolve_binary(self) -> str:
        candidates = [
            self.cli_tool,
            str(Path.home() / ".local" / "bin" / self.cli_tool),
            f"/usr/local/bin/{self.cli_tool}",
            f"/opt/homebrew/bin/{self.cli_tool}"
        ]
        for c in candidates:
            resolved = shutil.which(c)
            if resolved:
                return resolved
        return self.cli_tool

    def _call_api(self, text: str, source_lang: str, target_lang: str, mode: str = "auto") -> str:
        src_name = get_language_name(source_lang)
        tgt_name = get_language_name(target_lang)

        if mode == "auto":
            mode = "prompt" if target_lang.lower() in ("en", "english") else "response"

        # 1 single dedicated self-contained prompt per variant with all parameters baked in
        template = self.prompts.get(mode) or self.prompts.get("response") or self.system_prompt
        try:
            full_prompt = template.format(
                source_lang=src_name,
                target_lang=tgt_name,
                text=text
            )
        except Exception:
            full_prompt = f"{template}\n\nTask: Translate from {src_name} to {tgt_name}.\n\nTEXT:\n{text}"

        binary = self._resolve_binary()
        cmd = [binary]

        if self.cli_tool == "agy":
            cmd.append("--disable-slash-commands")
            model_to_use = self.model if (self.model and self.model not in ("default", "auto")) else "gemini-3.8-flash-low"
            cmd.extend(["--model", model_to_use])
        elif self.cli_tool == "claude":
            if self.model and self.model not in ("default", "auto"):
                cmd.extend(["--model", self.model])

        cmd.extend(["-p", full_prompt])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                raise RuntimeError(f"CLI tool returned empty stdout. Stderr: {result.stderr}")
            return output
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() if e.stderr else str(e)
            raise RuntimeError(f"CLI translation failed via '{binary}': {err}")
        except FileNotFoundError:
            raise RuntimeError(f"CLI tool '{self.cli_tool}' not found. Please ensure it is installed.")
