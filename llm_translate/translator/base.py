import re
from abc import ABC, abstractmethod
from typing import List

LANGUAGE_NAMES = {
    "uk": "Ukrainian",
    "ua": "Ukrainian",
    "en": "English",
    "pl": "Polish",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "zh": "Chinese",
    "tr": "Turkish",
    "cs": "Czech",
    "nl": "Dutch",
}

def get_language_name(code_or_name: str) -> str:
    cleaned = code_or_name.strip().lower()
    return LANGUAGE_NAMES.get(cleaned, code_or_name)

def chunk_markdown_text(text: str, max_chunk_size: int = 7500) -> List[str]:
    """
    Splits large markdown text into logical chunks along header/section boundaries,
    strictly respecting code fences so code blocks are NEVER cut in half.
    """
    if len(text) <= max_chunk_size:
        return [text]

    lines = text.splitlines(keepends=True)
    chunks = []
    current_lines = []
    current_len = 0
    in_code = False
    fence_char = None
    fence_len = 0

    for line in lines:
        stripped = line.strip()
        # Track fenced code blocks (``` or ~~~)
        if stripped.startswith("```") or stripped.startswith("~~~"):
            char = stripped[0]
            count = len(stripped) - len(stripped.lstrip(char))
            if not in_code:
                in_code = True
                fence_char = char
                fence_len = count
            elif char == fence_char and count >= fence_len:
                in_code = False
                fence_char = None
                fence_len = 0

        # Split points are ONLY allowed outside of code blocks
        is_split = (not in_code) and (
            stripped.startswith("# ") or 
            stripped.startswith("## ") or 
            stripped == "---"
        )

        if is_split and current_len >= 4500:
            chunks.append("".join(current_lines))
            current_lines = [line]
            current_len = len(line)
        else:
            current_lines.append(line)
            current_len += len(line)

    if current_lines:
        chunks.append("".join(current_lines))

    return chunks

MATH_BOX_CHARS = set("─━┌┐└┘├┤┬┴┼│║╔╗╚╝╠╣╦╩╬⎡⎢⎣⎤⎥⎦⎛⎜⎝⎞⎟⎠⌠⌡")

def is_pure_math_box_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    # Markdown horizontal rules, headers, bullets, or blockquotes
    if re.match(r"^[-─━_*]{3,}$", stripped):
        return False
    if stripped.startswith(("#", "•", "* ", "- ", "+ ", ">")):
        return False
    if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3:
        return False
    return any(c in MATH_BOX_CHARS for c in line)

class CodeShield:
    """
    Shields fenced code blocks, LaTeX display math, and multi-line ASCII/Unicode math blocks
    from being modified, reformatted, or corrupted during AI translation.
    """
    @classmethod
    def mask(cls, text: str):
        placeholders = {}
        counter = 0

        # 1. Mask fenced code blocks (```...``` and ~~~...~~~)
        def mask_code_block(m):
            nonlocal counter
            tok = f"__PROTECTED_CODE_BLOCK_{counter}__"
            placeholders[tok] = m.group(0)
            counter += 1
            return tok

        text = re.sub(r'(```[\s\S]*?```|~~~[\s\S]*?~~~)', mask_code_block, text)

        # 2. Mask display LaTeX blocks ($$...$$ and \[...\])
        def mask_math_block(m):
            nonlocal counter
            tok = f"__PROTECTED_MATH_BLOCK_{counter}__"
            placeholders[tok] = m.group(0)
            counter += 1
            return tok

        text = re.sub(r'(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\])', mask_math_block, text)

        # 3. Mask multi-line ASCII / Unicode math art
        lines = text.splitlines()
        new_lines = []
        in_block = False
        current_block = []

        for line in lines:
            is_math = is_pure_math_box_line(line)
            # Indented continuation lines under fraction bars or matrices
            if not is_math and in_block and line.startswith("    ") and line.strip() and not line.strip().startswith(("#", "•", "*", "-", ">")):
                is_math = True

            if is_math:
                if not in_block:
                    in_block = True
                    current_block = [line]
                else:
                    current_block.append(line)
            else:
                if in_block:
                    tok = f"__PROTECTED_ASCII_BLOCK_{counter}__"
                    placeholders[tok] = "\n".join(current_block)
                    counter += 1
                    new_lines.append(tok)
                    in_block = False
                    current_block = []
                new_lines.append(line)

        if in_block:
            tok = f"__PROTECTED_ASCII_BLOCK_{counter}__"
            placeholders[tok] = "\n".join(current_block)
            counter += 1
            new_lines.append(tok)

        return "\n".join(new_lines), placeholders

    @classmethod
    def unmask(cls, text: str, placeholders: dict) -> str:
        for tok, original in placeholders.items():
            text = text.replace(tok, original)
        return text

class BaseTranslator(ABC):
    def __init__(self, system_prompt: str = "", model: str = "", base_url: str = "", api_key: str = "", prompts: dict = None):
        self.system_prompt = system_prompt
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.prompts = prompts or {}

    @abstractmethod
    def _call_api(self, text: str, source_lang: str, target_lang: str, mode: str = "auto") -> str:
        pass

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "en", mode: str = "auto") -> str:
        if not text or not text.strip():
            return text

        # Protect code, LaTeX, and ASCII math blocks before calling AI model
        masked_text, placeholders = CodeShield.mask(text)

        chunks = chunk_markdown_text(masked_text, max_chunk_size=7500)
        if len(chunks) == 1:
            translated = self._call_api(masked_text, source_lang, target_lang, mode=mode)
            return CodeShield.unmask(translated, placeholders)

        translated_chunks = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            translated_chunk = self._call_api(chunk, source_lang, target_lang, mode=mode)
            translated_chunks.append(translated_chunk)

        result = "\n\n".join(translated_chunks)
        return CodeShield.unmask(result, placeholders)
