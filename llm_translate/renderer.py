import re
import shutil
import unicodedata
from typing import List, Optional

# ANSI Color constants
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
STRIKETHROUGH = "\033[9m"

# Colors matching Antigravity palette
CYAN = "\033[36m"
BRIGHT_CYAN = "\033[96m"
GREEN = "\033[32m"
BRIGHT_GREEN = "\033[92m"
YELLOW = "\033[33m"
BRIGHT_YELLOW = "\033[93m"
MAGENTA = "\033[35m"
BRIGHT_MAGENTA = "\033[95m"
BLUE = "\033[34m"
BRIGHT_BLUE = "\033[94m"
RED = "\033[31m"
BRIGHT_RED = "\033[91m"
GRAY = "\033[90m"
WHITE = "\033[97m"

# Backgrounds
CODE_FG = "\033[38;5;215m"  # Warm amber
KBD_BG = "\033[48;5;238m"

KEYWORDS = {
    "def", "class", "import", "from", "return", "if", "else", "elif",
    "for", "while", "try", "except", "finally", "with", "as", "async",
    "await", "lambda", "yield", "raise", "break", "continue", "pass",
    "function", "const", "let", "var", "interface", "type", "export",
    "default", "case", "switch", "true", "false", "null", "None", "True",
    "False", "pub", "struct", "impl", "fn", "mut", "use", "mod", "enum",
    "SELECT", "FROM", "WHERE", "JOIN", "INSERT", "UPDATE", "DELETE"
}

ALERT_STYLES = {
    "NOTE": (BRIGHT_BLUE, "Note"),
    "TIP": (BRIGHT_GREEN, "Tip"),
    "IMPORTANT": (BRIGHT_MAGENTA, "Important"),
    "WARNING": (BRIGHT_YELLOW, "Warning"),
    "CAUTION": (BRIGHT_RED, "Caution")
}

MATH_SYMBOLS = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\varepsilon": "ε", r"\epsilon": "ε", r"\zeta": "ζ", r"\eta": "η",
    r"\theta": "θ", r"\vartheta": "ϑ", r"\iota": "ι", r"\kappa": "κ",
    r"\lambda": "λ", r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ",
    r"\pi": "π", r"\rho": "ρ", r"\varrho": "ϱ", r"\sigma": "σ",
    r"\tau": "τ", r"\upsilon": "υ", r"\phi": "ϕ", r"\varphi": "φ",
    r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ",
    r"\Xi": "Ξ", r"\Pi": "Π", r"\Sigma": "Σ", r"\Upsilon": "Υ",
    r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
    r"\sum": "∑", r"\prod": "∏", r"\coprod": "∐", r"\int": "∫",
    r"\iint": "∬", r"\iiint": "∭", r"\oint": "∮",
    r"\infty": "∞", r"\approx": "≈", r"\neq": "≠", r"\leq": "≤",
    r"\geq": "≥", r"\pm": "±", r"\times": "×", r"\div": "÷",
    r"\cdot": "·", r"\partial": "∂", r"\nabla": "∇", r"\in": "∈",
    r"\notin": "∉", r"\subset": "⊂", r"\supset": "⊃", r"\cup": "∪",
    r"\cap": "∩", r"\forall": "∀", r"\exists": "∃", r"\to": "→",
    r"\rightarrow": "→", r"\leftarrow": "←", r"\Rightarrow": "⇒",
    r"\Leftarrow": "⇐", r"\leftrightarrow": "↔", r"\cdots": "⋯",
    r"\vdots": "⋮", r"\ddots": "⋱", r"\ell": "ℓ", r"\hbar": "ℏ",
    r"\degree": "°", r"\circ": "°",
    r"\exp": "exp", r"\log": "log", r"\ln": "ln", r"\sin": "sin",
    r"\cos": "cos", r"\tan": "tan", r"\det": "det", r"\lim": "lim",
    r"\min": "min", r"\max": "max",
    r"\Longleftrightarrow": "⟺", r"\Longrightarrow": "⟹",
    r"\longleftrightarrow": "⟺", r"\longrightarrow": "⟶",
    r"\iff": "⟺", r"\implies": "⟹",
    r"\dots": "…", r"\ldots": "…", r"\cdots": "⋯", r"\vdots": "⋮", r"\ddots": "⋱",
    r"\mid": "|", r"\Concat": "Concat", r"\MultiHead": "MultiHead",
    r"\Attention": "Attention", r"\softmax": "softmax", r"\where": "where",
    r"\sim": "∼", r"\operatorname{Cov}": "Cov", r"\operatorname{det}": "det",
    r"\operatorname{Var}": "Var", r"\operatornameCₒᵥ": "Cov", r"\operatorname": "",
    r"\quad": "  ", r"\qquad": "    ", r"\,": " ", r"\:": " ", r"\;": " ", r"\!": ""
}

MATH_FONTS = {}
# Math bold uppercase A-Z (0x1D400)
for _i in range(26):
    MATH_FONTS[f"\\mathbf{{{chr(65+_i)}}}"] = chr(0x1D400 + _i)
    MATH_FONTS[f"\\boldsymbol{{{chr(65+_i)}}}"] = chr(0x1D400 + _i)
# Math bold lowercase a-z (0x1D41A)
for _i in range(26):
    MATH_FONTS[f"\\mathbf{{{chr(97+_i)}}}"] = chr(0x1D41A + _i)
    MATH_FONTS[f"\\boldsymbol{{{chr(97+_i)}}}"] = chr(0x1D41A + _i)
# Math bold digits 0-9 (0x1D7CE)
for _i in range(10):
    MATH_FONTS[f"\\mathbf{{{chr(48+_i)}}}"] = chr(0x1D7CE + _i)
    MATH_FONTS[f"\\boldsymbol{{{chr(48+_i)}}}"] = chr(0x1D7CE + _i)

# Greek bold & standard
GREEK_BOLD = {
    r"\mu": "𝛍", r"\Sigma": "𝚺", r"\sigma": "𝛔", r"\theta": "𝛉", r"\alpha": "𝛂",
    r"\beta": "𝛃", r"\gamma": "𝛄", r"\delta": "𝛅", r"\lambda": "𝛌", r"\omega": "𝛚",
    r"\pi": "𝛑", r"\phi": "𝛗", r"\psi": "𝛙", r"\xi": "𝛏", r"\zeta": "𝛇", r"\eta": "𝛈",
    "mu": "𝛍", "Sigma": "𝚺", "sigma": "𝛔", "theta": "𝛉", "alpha": "𝛂", "beta": "𝛃", "gamma": "𝛄", "delta": "𝛅",
    "lambda": "𝛌", "omega": "𝛚", "pi": "𝛑", "phi": "𝛗", "psi": "𝛙", "xi": "𝛏", "zeta": "𝛇", "eta": "𝛈",
    "μ": "𝛍", "Σ": "𝚺", "σ": "𝛔", "θ": "𝛉", "α": "𝛂", "β": "𝛃", "γ": "𝛄", "δ": "𝛅",
    "λ": "𝛌", "ω": "𝛚", "π": "𝛑", "ϕ": "𝛗", "φ": "𝛗", "ψ": "𝛙", "ξ": "𝛏"
}
for k, v in GREEK_BOLD.items():
    MATH_FONTS[f"\\boldsymbol{{{k}}}"] = v
    MATH_FONTS[f"\\mathbf{{{k}}}"] = v

MATH_FONTS.update({
    r"\mathcal{L}": "ℒ", r"\mathcal{H}": "ℋ", r"\mathcal{F}": "ℱ",
    r"\mathcal{N}": "𝒩", r"\mathcal{O}": "𝒪", r"\mathcal{P}": "𝒫",
    r"\mathbb{R}": "ℝ", r"\mathbb{E}": "𝔼", r"\mathbb{N}": "ℕ",
    r"\mathbb{Z}": "ℤ", r"\mathbb{C}": "ℂ", r"\mathbb{Q}": "ℚ",
    r"\mathbb{P}": "ℙ", r"\mathbbR": "ℝ", r"\mathbbE": "𝔼",
    r"\boldsymbol{\ell}": "ℓ",
    r"\hat{y}": "ŷ", r"\hat{x}": "x̂", r"\hat{z}": "ẑ",
    r"\vec{v}": "v⃗", r"\vec{x}": "x⃗"
})

SUBS = {
    "0":"₀","1":"₁","2":"₂","3":"₃","4":"₄","5":"₅","6":"₆","7":"₇","8":"₈","9":"₉",
    "a":"ₐ","e":"ₑ","h":"ₕ","i":"ᵢ","j":"ⱼ","k":"ₖ","l":"ₗ","m":"ₘ","n":"ₙ","o":"ₒ",
    "p":"ₚ","r":"ᵣ","s":"ₛ","t":"ₜ","u":"ᵤ","v":"ᵥ","x":"ₓ","y":"ᵧ",
    "+":"₊","-":"₋","=":"₌","(":"₍",")":"₎"
}
SUPS = {
    "0":"⁰","1":"¹","2":"²","3":"³","4":"⁴","5":"⁵","6":"⁶","7":"⁷","8":"⁸","9":"⁹",
    "a":"ᵃ","b":"ᵇ","c":"ᶜ","d":"ᵈ","e":"ᵉ","f":"ᶠ","g":"ᵍ","h":"ʰ","i":"ⁱ","j":"ʲ",
    "k":"ᵏ","l":"ˡ","m":"ᵐ","n":"ⁿ","o":"ᵒ","p":"ᵖ","r":"ʳ","s":"ˢ","t":"ᵗ","u":"ᵘ",
    "v":"ᵛ","w":"ʷ","x":"ˣ","y":"ʸ","z":"ᶻ",
    "A":"ᴬ","B":"ᴮ","D":"ᴰ","E":"ᴱ","G":"ᴳ","H":"ᴴ","I":"ᴵ","J":"ᴶ","K":"ᴷ","L":"ᴸ",
    "M":"ᴹ","N":"ᴺ","O":"ᴼ","P":"ᴾ","R":"ᴿ","T":"ᵀ","U":"ᵁ","V":"ⱽ","W":"ᵂ",
    "Q":"ᑫ",
    "+":"⁺","-":"⁻","=":"⁼","(":"⁽",")":"⁾","/":"ᐟ"
}

def str_display_width(s: str) -> int:
    """Accurately calculates column width in terminal display cells."""
    s = re.sub(r'\033\[[0-9;]*[a-zA-Z]', '', s)
    s = re.sub(r'\033\]8;;[^\033]*\033\\', '', s)
    w = 0
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        if eaw in ('W', 'F') or ord(ch) >= 0x1F300:
            w += 2
        elif ord(ch) < 32 or (0x7F <= ord(ch) < 0xA0):
            continue
        else:
            w += 1
    return w

def highlight_syntax(code_line: str, lang: str = "") -> str:
    """Applies syntax highlighting matching Antigravity CLI."""
    if lang == "diff":
        if code_line.startswith("+"):
            return f"{BRIGHT_GREEN}{code_line}{RESET}"
        elif code_line.startswith("-"):
            return f"{BRIGHT_RED}{code_line}{RESET}"
        elif code_line.startswith("@@"):
            return f"{CYAN}{code_line}{RESET}"
        return f"{GRAY}{code_line}{RESET}"

    # Comments
    if code_line.strip().startswith(("#", "//", "--")):
        return f"{GRAY}{code_line}{RESET}"

    # Strings
    def color_string(match):
        return f"{GREEN}{match.group(0)}{RESET}"

    line = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', color_string, code_line)

    # Keywords
    def color_keyword(match):
        word = match.group(0)
        if word in KEYWORDS:
            return f"{MAGENTA}{BOLD}{word}{RESET}"
        return word

    line = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', color_keyword, line)

    # Numbers
    line = re.sub(r'\b\d+(?:\.\d+)?\b', lambda m: f"{YELLOW}{m.group(0)}{RESET}", line)

    return line

def clean_latex_math(text: str) -> str:
    """Converts LaTeX math expressions into clean terminal Unicode."""
    text = re.sub(r'\\(?:big|Big|bigg|Bigg)[glr]?', '', text)
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)

    # Normalize braces & spaces in font/style macros
    text = re.sub(r'\\(mathbf|boldsymbol|hat|vec|mathcal|mathrm|text)\s*\{\s*\\?([^{}]+?)\s*\}', lambda m: f"\\{m.group(1)}{{{m.group(2).strip()}}}", text)
    text = re.sub(r'\\(mathbf|boldsymbol)\s*([0-9a-zA-Z])(?![a-zA-Z])', r'\\\1{\2}', text)

    # Unicode Greek letters inside \boldsymbol or \mathbf
    for k, v in GREEK_BOLD.items():
        text = text.replace(f"\\boldsymbol{{{k}}}", v).replace(f"\\mathbf{{{k}}}", v)

    # Hats: \hat{f} -> f̂
    text = re.sub(r'\\hat\s*\{\s*([a-zA-Zα-ωΑ-Ω])\s*\}', r'\1̂', text)
    text = re.sub(r'\\hat\s+([a-zA-Zα-ωΑ-Ω])(?![a-zA-Z])', r'\1̂', text)

    # Transpose ^T, ^\top, ^\intercal, or )T
    text = re.sub(r'\^\s*\{?\s*(?:T|\\top|\\intercal)\s*\}?', 'ᵀ', text)
    text = re.sub(r'\)\s*T(?=\s|[,\);|]|$)', ')ᵀ', text)

    # Inverse ^{-1} -> ⁻¹
    text = re.sub(r'\^\s*\{?\s*-1\s*\}?', '⁻¹', text)
    text = re.sub(r'\^\s*\{?\s*D/2\s*\}?', 'ᴰ/²', text)
    text = re.sub(r'\^\s*\{?\s*1/2\s*\}?', '¹/²', text)

    # 1. Fonts & Accents
    for k in sorted(MATH_FONTS.keys(), key=len, reverse=True):
        text = text.replace(k, MATH_FONTS[k])
    # 2. Math symbols
    for k in sorted(MATH_SYMBOLS.keys(), key=len, reverse=True):
        text = text.replace(k, MATH_SYMBOLS[k])
    
    text = re.sub(r'√\{([^}]+)\}', r'√(\1)', text)
    
    # 3. Fractions \frac{A}{B} handling nested braces
    while r"\frac" in text:
        m = re.search(r"\\frac\{", text)
        if not m:
            break
        start = m.start()
        idx = m.end()
        depth = 1
        num = []
        while idx < len(text) and depth > 0:
            if text[idx] == '{': depth += 1
            elif text[idx] == '}': depth -= 1
            if depth > 0: num.append(text[idx])
            idx += 1
        if idx >= len(text) or text[idx] != '{':
            break
        idx += 1
        depth = 1
        den = []
        while idx < len(text) and depth > 0:
            if text[idx] == '{': depth += 1
            elif text[idx] == '}': depth -= 1
            if depth > 0: den.append(text[idx])
            idx += 1
        num_str = "".join(num)
        den_str = "".join(den)
        text = text[:start] + f"({num_str})/({den_str})" + text[idx:]

    # 4. Subscripts & Superscripts
    text = re.sub(r'_\{([0-9a-zA-Z+\-=()]+)\}', lambda m: "".join(SUBS.get(c, c) for c in m.group(1)), text)
    text = re.sub(r'(?<![\\a-zA-Z])([a-zA-Zα-ωΑ-Ω])\{([0-9a-zA-Z]+)\}', lambda m: m.group(1) + "".join(SUBS.get(c, c) for c in m.group(2)), text)
    text = re.sub(r'_([0-9a-zA-Z])', lambda m: SUBS.get(m.group(1), m.group(1)), text)
    text = re.sub(r'_\{([^}]+)\}', r'_\1', text)  # Fallback for complex subscripts e.g. _𝐖
    text = re.sub(r'\^\{([0-9a-zA-Z+\-=()]+)\}', lambda m: "".join(SUPS.get(c, c) for c in m.group(1)), text)
    text = re.sub(r'\^([0-9a-zA-Z])', lambda m: SUPS.get(m.group(1), m.group(1)), text)
    
    # Clean operator and blackboard wrappers
    text = re.sub(r'\\operatorname\s*\{\s*([^{}]+?)\s*\}', r'\1', text)
    text = re.sub(r'\\operatorname\s+([a-zA-Z]+)', r'\1', text)
    text = re.sub(r'\\mathbb\s*\{\s*([a-zA-Z])\s*\}', lambda m: MATH_FONTS.get(f"\\mathbb{{{m.group(1)}}}", m.group(1)), text)

    # 5. Clean brackets without stripping the bracket characters
    text = re.sub(r'\\(?:left|right)(?=[()\[\]|])', '', text)
    text = re.sub(r'\\(?:left|right)\.?', '', text)
    text = text.replace("{", "").replace("}", "")
    return text.strip()

def clean_inline_latex(text: str) -> str:
    """Cleans LaTeX math macros and syntax found outside math blocks or in mixed text."""
    # 1. Unescape Unicode brackets and parens
    text = re.sub(r'\\([⎛⎝⎜⎞⎠⎟⎡⎣⎢⎤⎦⎥⌠⌡│()\[\]])', r'\1', text)

    has_latex = "\\" in text or "^" in text or "{" in text or "_" in text
    if not has_latex:
        return text

    # Normalize font macros: \boldsymbol { μ } -> \boldsymbol{μ}
    text = re.sub(r'\\(mathbf|boldsymbol|hat|vec|mathcal|mathrm|text)\s*\{\s*\\?([^{}]+?)\s*\}', lambda m: f"\\{m.group(1)}{{{m.group(2).strip()}}}", text)
    text = re.sub(r'\\(mathbf|boldsymbol)\s*([0-9a-zA-Z])(?![a-zA-Z])', r'\\\1{\2}', text)

    # Greek bold mappings
    for k, v in GREEK_BOLD.items():
        text = text.replace(f"\\boldsymbol{{{k}}}", v).replace(f"\\mathbf{{{k}}}", v)

    # Accents: \hat, \vec
    text = re.sub(r'\\hat\s*\{\s*([a-zA-Zα-ωΑ-Ω])\s*\}', r'\1̂', text)
    text = re.sub(r'\\hat\s+([a-zA-Zα-ωΑ-Ω])(?![a-zA-Z])', r'\1̂', text)
    text = re.sub(r'\\vec\s*\{\s*([a-zA-Zα-ωΑ-Ω])\s*\}', r'\1⃗', text)

    # Transpose and common powers
    text = re.sub(r'\^\s*\{?\s*(?:T|\\top|\\intercal)\s*\}?', 'ᵀ', text)
    text = re.sub(r'\)\s*T(?=\s|[,\);|]|$)', ')ᵀ', text)
    text = re.sub(r'\^\s*\{?\s*-1\s*\}?', '⁻¹', text)
    text = re.sub(r'\^\s*\{?\s*D/2\s*\}?', 'ᴰ/²', text)
    text = re.sub(r'\^\s*\{?\s*1/2\s*\}?', '¹/²', text)

    # Fonts & Symbols
    for k in sorted(MATH_FONTS.keys(), key=len, reverse=True):
        text = text.replace(k, MATH_FONTS[k])
    for k in sorted(MATH_SYMBOLS.keys(), key=len, reverse=True):
        text = text.replace(k, MATH_SYMBOLS[k])

    # Fractions \frac{A}{B}
    while r"\frac" in text:
        m = re.search(r"\\frac\{", text)
        if not m:
            break
        start, idx, depth, num = m.start(), m.end(), 1, []
        while idx < len(text) and depth > 0:
            if text[idx] == '{': depth += 1
            elif text[idx] == '}': depth -= 1
            if depth > 0: num.append(text[idx])
            idx += 1
        if idx >= len(text) or text[idx] != '{':
            break
        idx, depth, den = idx + 1, 1, []
        while idx < len(text) and depth > 0:
            if text[idx] == '{': depth += 1
            elif text[idx] == '}': depth -= 1
            if depth > 0: den.append(text[idx])
            idx += 1
        num_clean = clean_inline_latex("".join(num))
        den_clean = clean_inline_latex("".join(den))
        text = text[:start] + f"({num_clean})/({den_clean})" + text[idx:]

    # Subscripts: explicit braces _\{...\} or complex braces like a{11} or single-char with lookbehind
    text = re.sub(r'_\{([0-9a-zA-Z+\-=()]+)\}', lambda m: "".join(SUBS.get(c, c) for c in m.group(1)), text)
    text = re.sub(r'(?<![\\a-zA-Z])([a-zA-Zα-ωΑ-Ω])\{([0-9a-zA-Z]+)\}', lambda m: m.group(1) + "".join(SUBS.get(c, c) for c in m.group(2)), text)
    text = re.sub(r'(?<=[a-zA-Z0-9\)])_([0-9a-zA-Z])(?![a-zA-Z0-9])', lambda m: SUBS.get(m.group(1), m.group(0)), text)

    # Superscripts: explicit braces ^\{...\} or single-char with lookbehind
    text = re.sub(r'\^\{([0-9a-zA-Z+\-=()]+)\}', lambda m: "".join(SUPS.get(c, c) for c in m.group(1)), text)
    text = re.sub(r'(?<=[a-zA-Z0-9\)])\^([0-9a-zA-Z])(?![a-zA-Z0-9])', lambda m: SUPS.get(m.group(1), m.group(0)), text)

    # Clean leftover LaTeX wrappers
    text = re.sub(r'\\operatorname\s*\{\s*([^{}]+?)\s*\}', r'\1', text)
    text = re.sub(r'\\operatorname\s+([a-zA-Z]+)', r'\1', text)
    text = re.sub(r'\\mathbb\s*\{\s*([a-zA-Z])\s*\}', lambda m: MATH_FONTS.get(f"\\mathbb{{{m.group(1)}}}", m.group(1)), text)
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\(?:left|right)(?=[()\[\]|])', '', text)
    text = re.sub(r'\\(?:left|right)\.?', '', text)

    return text

class Box:
    def __init__(self, lines, baseline=0):
        self.lines = list(lines) if lines else [""]
        self.baseline = baseline
        self.width = max((str_display_width(l) for l in self.lines), default=0)

def concat_boxes(*boxes, space="") -> Box:
    valid = [b for b in boxes if b and b.lines and b.width > 0]
    if not valid:
        return Box([""])
    max_above = max(b.baseline for b in valid)
    max_below = max(len(b.lines) - 1 - b.baseline for b in valid)
    total_h = max_above + 1 + max_below

    padded_boxes = []
    for b in valid:
        lines_above = max_above - b.baseline
        lines_below = max_below - (len(b.lines) - 1 - b.baseline)
        padded = ([" " * b.width] * lines_above) + [l + " " * (b.width - str_display_width(l)) for l in b.lines] + ([" " * b.width] * lines_below)
        padded_boxes.append(padded)

    res_lines = []
    for row in range(total_h):
        row_str = space.join(padded_boxes[i][row] for i in range(len(padded_boxes)))
        res_lines.append(row_str)
    return Box(res_lines, baseline=max_above)

def make_fraction(num_box: Box, den_box: Box) -> Box:
    w = max(num_box.width, den_box.width) + 2
    bar = "─" * w
    num_padded = [(" " * ((w - str_display_width(l)) // 2)) + l + (" " * (w - str_display_width(l) - (w - str_display_width(l)) // 2)) for l in num_box.lines]
    den_padded = [(" " * ((w - str_display_width(l)) // 2)) + l + (" " * (w - str_display_width(l) - (w - str_display_width(l)) // 2)) for l in den_box.lines]
    lines = num_padded + [bar] + den_padded
    baseline = len(num_padded)
    return Box(lines, baseline)

def make_bracket(b: Box, b_type: str = "paren", exponent_box: Box = None) -> Box:
    h = len(b.lines)
    open_c = "|" if b_type == "pipe" else ("[" if b_type == "bracket" else ("(" if b_type == "paren" else "{"))
    close_c = "|" if b_type == "pipe" else ("]" if b_type == "bracket" else (")" if b_type == "paren" else "}"))

    # If single-line inside, check if exponent needs a second line
    if h == 1:
        single_bracket = Box([f"{open_c}{b.lines[0]}{close_c}"], b.baseline)
        if exponent_box and exponent_box.lines and any(exponent_box.lines):
            exp_text = exponent_box.lines[0].strip()
            # If exponent is a single unicode superscript character, attach inline
            if len(exp_text) == 1 and (exp_text in "⁰¹²³⁴⁵⁶⁷⁸⁹ᵀ⁻⁺" or ord(exp_text) >= 0x2070):
                return Box([f"{open_c}{b.lines[0]}{close_c}{exp_text}"], b.baseline)
            else:
                # Multi-character exponent (like k/2, D/2, 1/2) is rendered on the line ABOVE!
                w_base = single_bracket.width
                exp_w = str_display_width(exp_text)
                lines = [
                    " " * w_base + exp_text,
                    single_bracket.lines[0] + " " * exp_w
                ]
                return Box(lines, baseline=1)
        return single_bracket

    new_lines = []
    if b_type == "pipe":
        new_lines = [f"│ {l} │" for l in b.lines]
    elif b_type == "bracket":
        if h == 2:
            new_lines.append(f"⎡{b.lines[0]}⎤")
            new_lines.append(f"⎣{b.lines[1]}⎦")
        else:
            new_lines.append(f"⎡ {b.lines[0]} ⎤")
            for l in b.lines[1:-1]:
                new_lines.append(f"⎢ {l} ⎥")
            new_lines.append(f"⎣ {b.lines[-1]} ⎦")
    else:
        if h == 2:
            new_lines.append(f"⎛{b.lines[0]}⎞")
            new_lines.append(f"⎝{b.lines[1]}⎠")
        else:
            new_lines.append(f"⎛ {b.lines[0]} ⎞")
            for l in b.lines[1:-1]:
                new_lines.append(f"⎜ {l} ⎟")
            new_lines.append(f"⎝ {b.lines[-1]} ⎠")

    bracket_box = Box(new_lines, b.baseline)
    if exponent_box:
        exp_lines = exponent_box.lines
        exp_w = exponent_box.width
        combined_lines = []
        for r in range(len(bracket_box.lines)):
            if r < len(exp_lines):
                combined_lines.append(bracket_box.lines[r] + exp_lines[r])
            else:
                combined_lines.append(bracket_box.lines[r] + " " * exp_w)
        return Box(combined_lines, bracket_box.baseline)
    return bracket_box

def attach_sub_sup(base_box: Box, sup_box: Box = None, sub_box: Box = None) -> Box:
    if not sup_box and not sub_box:
        return base_box

    if len(base_box.lines) == 1:
        w_base = base_box.width
        w_sup = sup_box.width if sup_box else 0
        w_sub = sub_box.width if sub_box else 0
        w_max = max(w_base, w_sup, w_sub)

        lines = []
        if sup_box and sub_box:
            lines.append((sup_box.lines[0] if sup_box.lines else "") + " " * (w_max - w_sup))
            lines.append(base_box.lines[0] + " " * (w_max - w_base))
            lines.append((sub_box.lines[0] if sub_box.lines else "") + " " * (w_max - w_sub))
            return Box(lines, baseline=1)
        elif sup_box:
            lines.append((sup_box.lines[0] if sup_box.lines else "") + " " * (w_max - w_sup))
            lines.append(base_box.lines[0] + " " * (w_max - w_base))
            return Box(lines, baseline=1)
        elif sub_box:
            lines.append(base_box.lines[0] + " " * (w_max - w_base))
            lines.append((sub_box.lines[0] if sub_box.lines else "") + " " * (w_max - w_sub))
            return Box(lines, baseline=0)

    res = base_box
    if sup_box:
        sup_shifted = Box(sup_box.lines, baseline=len(sup_box.lines))
        res = concat_boxes(res, sup_shifted)
    if sub_box:
        sub_shifted = Box(sub_box.lines, baseline=-1)
        res = concat_boxes(res, sub_shifted)
    return res

def parse_latex_to_box(text: str) -> Box:
    text = text.strip()
    text = re.sub(r'\\(?:big|Big|bigg|Bigg)[glr]?', '', text)
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)

    # Normalize braces & spaces in font/style macros
    text = re.sub(r'\\(mathbf|boldsymbol|hat|vec|mathcal|mathrm|text)\s*\{\s*\\?([^{}]+?)\s*\}', lambda m: f"\\{m.group(1)}{{{m.group(2).strip()}}}", text)
    text = re.sub(r'\\(mathbf|boldsymbol)\s*([0-9a-zA-Z])(?![a-zA-Z])', r'\\\1{\2}', text)

    # Unicode Greek letters inside \boldsymbol or \mathbf
    for k, v in GREEK_BOLD.items():
        text = text.replace(f"\\boldsymbol{{{k}}}", v).replace(f"\\mathbf{{{k}}}", v)

    # Hats: \hat{f} -> f̂
    text = re.sub(r'\\hat\s*\{\s*([a-zA-Zα-ωΑ-Ω])\s*\}', r'\1̂', text)
    text = re.sub(r'\\hat\s+([a-zA-Zα-ωΑ-Ω])(?![a-zA-Z])', r'\1̂', text)

    # Transpose ^T, ^\top, ^\intercal, or )T
    text = re.sub(r'\^\s*\{?\s*(?:T|\\top|\\intercal)\s*\}?', 'ᵀ', text)
    text = re.sub(r'\)\s*T(?=\s|[,\);|]|$)', ')ᵀ', text)

    # Inverse ^{-1} -> ⁻¹
    text = re.sub(r'\^\s*\{?\s*-1\s*\}?', '⁻¹', text)

    for k in sorted(MATH_FONTS.keys(), key=len, reverse=True):
        text = text.replace(k, MATH_FONTS[k])
    for k in sorted(MATH_SYMBOLS.keys(), key=len, reverse=True):
        text = text.replace(k, MATH_SYMBOLS[k])

    text = re.sub(r'√\{([^}]+)\}', r'√(\1)', text)

    i = 0
    n = len(text)

    def extract_braced(idx):
        if idx >= n:
            return "", idx
        if text[idx] != '{':
            return text[idx], idx + 1
        idx += 1
        depth = 1
        start = idx
        while idx < n and depth > 0:
            if text[idx] == '{': depth += 1
            elif text[idx] == '}': depth -= 1
            idx += 1
        return text[start:idx-1], idx

    def extract_paren(idx):
        is_left = text[idx:].startswith(r"\left(") or text[idx:].startswith(r"\left[") or text[idx:].startswith(r"\left|")
        if is_left:
            idx += 6
            if text[idx-6:].startswith(r"\left("):
                open_pat, close_pat = r"\left(", r"\right)"
            elif text[idx-6:].startswith(r"\left["):
                open_pat, close_pat = r"\left[", r"\right]"
            else:
                open_pat, close_pat = r"\left|", r"\right|"
        else:
            ch = text[idx]
            idx += 1
            if ch == "(": open_pat, close_pat = "(", ")"
            elif ch == "[": open_pat, close_pat = "[", "]"
            else: open_pat, close_pat = "|", "|"

        start = idx
        depth = 1
        while idx < n and depth > 0:
            if is_left and text[idx:].startswith(open_pat) and open_pat != close_pat:
                depth += 1
                idx += len(open_pat)
                continue
            elif is_left and text[idx:].startswith(close_pat):
                depth -= 1
                if depth == 0:
                    return text[start:idx], idx + len(close_pat)
                idx += len(close_pat)
                continue
            elif not is_left and open_pat == close_pat and text[idx] == close_pat:
                depth -= 1
                if depth == 0:
                    return text[start:idx], idx + 1
                idx += 1
                continue
            elif not is_left and text[idx] == open_pat:
                depth += 1
                idx += 1
                continue
            elif not is_left and text[idx] == close_pat:
                depth -= 1
                if depth == 0:
                    return text[start:idx], idx + 1
                idx += 1
                continue
            idx += 1
        return text[start:idx], idx

    boxes = []

    while i < n:
        if text[i].isspace():
            i += 1
            continue

        if text[i:].startswith(r"\frac"):
            i += 5
            while i < n and text[i].isspace(): i += 1
            num_str, i = extract_braced(i)
            while i < n and text[i].isspace(): i += 1
            den_str, i = extract_braced(i)

            num_box = parse_latex_to_box(num_str)
            den_box = parse_latex_to_box(den_str)
            boxes.append(make_fraction(num_box, den_box))
            continue

        if text[i:].startswith(r"\left(") or text[i:].startswith(r"\left[") or text[i:].startswith(r"\left|") or text[i] in "([|":
            if text[i:].startswith(r"\left|") or text[i] == '|':
                b_type = "pipe"
            elif text[i:].startswith(r"\left[") or text[i] == '[':
                b_type = "bracket"
            else:
                b_type = "paren"
            inner_str, i = extract_paren(i)
            inner_box = parse_latex_to_box(inner_str)

            exp_box = None
            if i < n and text[i] == '^':
                i += 1
                exp_str, i = extract_braced(i)
                exp_box = parse_latex_to_box(exp_str)

            bracket_box = make_bracket(inner_box, b_type=b_type, exponent_box=exp_box)
            if boxes and len(boxes[-1].lines) == 1 and boxes[-1].lines[0] in ("f", "exp", "log", "ln", "sin", "cos", "tan", "√"):
                boxes[-1] = concat_boxes(boxes[-1], bracket_box, space="")
            else:
                boxes.append(bracket_box)
            continue

        if text[i:].startswith(r"\left") or text[i:].startswith(r"\right"):
            i += 5
            continue

        if text[i] == '^':
            i += 1
            sup_str, i = extract_braced(i)
            if boxes and len(boxes[-1].lines) == 1 and boxes[-1].lines[0] not in ("∑", "∏", "∫") and all(c in SUPS for c in sup_str):
                sup_unicode = "".join(SUPS[c] for c in sup_str)
                boxes[-1] = Box([boxes[-1].lines[0] + sup_unicode], boxes[-1].baseline)
            else:
                sup_box = parse_latex_to_box(sup_str)
                if boxes:
                    boxes[-1] = attach_sub_sup(boxes[-1], sup_box=sup_box)
                else:
                    boxes.append(sup_box)
            continue

        if text[i] == '_':
            i += 1
            sub_str, i = extract_braced(i)
            if boxes and len(boxes[-1].lines) == 1 and boxes[-1].lines[0] not in ("∑", "∏", "∫") and all(c in SUBS for c in sub_str):
                sub_unicode = "".join(SUBS[c] for c in sub_str)
                boxes[-1] = Box([boxes[-1].lines[0] + sub_unicode], boxes[-1].baseline)
            else:
                sub_box = parse_latex_to_box(sub_str)
                if boxes:
                    boxes[-1] = attach_sub_sup(boxes[-1], sub_box=sub_box)
                else:
                    boxes.append(sub_box)
            continue

        token = ""
        while i < n and not text[i].isspace() and text[i] not in "^_(){}[];," and not text[i:].startswith(r"\frac") and not text[i:].startswith(r"\left") and not text[i:].startswith(r"\right"):
            token += text[i]
            i += 1
            if token in ("=", "+", "-", "·", "×", "±", "→", "⇒", "≠", "≤", "≥", "⟺", "⟹", "…", "⋯"):
                break
        if not token and i < n:
            token = text[i]
            i += 1
        if token:
            if token == ",":
                if boxes:
                    boxes[-1] = Box([boxes[-1].lines[0] + ","], boxes[-1].baseline)
                else:
                    boxes.append(Box([","], 0))
            else:
                boxes.append(Box([token], 0))

    if not boxes:
        return Box([""])

    return concat_boxes(*boxes, space=" ")

def render_matrix_equation(eq_text: str) -> List[str]:
    """Renders LaTeX matrix equations (bmatrix) into stacked Unicode terminal box drawings."""
    parts = re.split(r'\\begin\{(?:b|p|v|V)?matrix\}([\s\S]*?)\\end\{(?:b|p|v|V)?matrix\}', eq_text)
    blocks = []
    max_h = 1

    for idx, chunk in enumerate(parts):
        if idx % 2 == 1:
            rows = []
            for r in chunk.strip().split(r"\\"):
                r = r.strip()
                if not r:
                    continue
                cells = [clean_latex_math(c.strip()) for c in r.split("&")]
                rows.append(cells)
            if not rows:
                continue
            num_cols = max(len(r) for r in rows)
            col_w = [max(str_display_width(r[c]) if c < len(r) else 0 for r in rows) for c in range(num_cols)]
            n_r = len(rows)
            mat_lines = []
            for r_idx, r in enumerate(rows):
                formatted_cells = []
                for c in range(num_cols):
                    val = r[c] if c < len(r) else ""
                    pad = max(0, col_w[c] - str_display_width(val))
                    pad_l = pad // 2
                    pad_r = pad - pad_l
                    formatted_cells.append(" " * pad_l + val + " " * pad_r)
                fmt = "  ".join(formatted_cells)
                if n_r == 1:
                    mat_lines.append(f"[{fmt}]")
                elif r_idx == 0:
                    mat_lines.append(f"⎡ {fmt} ⎤")
                elif r_idx == n_r - 1:
                    mat_lines.append(f"⎣ {fmt} ⎦")
                else:
                    mat_lines.append(f"⎢ {fmt} ⎥")
            blocks.append(mat_lines)
            max_h = max(max_h, len(mat_lines))
        else:
            t = clean_latex_math(chunk).strip()
            if t:
                blocks.append([t])

    if not blocks:
        return [clean_latex_math(eq_text)]

    padded_blocks = []
    for b in blocks:
        h = len(b)
        w = max((str_display_width(l) for l in b), default=0)
        pad_top = (max_h - h) // 2
        pad_bot = max_h - h - pad_top
        new_b = [" " * w] * pad_top + b + [" " * w] * pad_bot
        padded_blocks.append(new_b)

    result = []
    for row_idx in range(max_h):
        line = " ".join(b[row_idx] for b in padded_blocks if any(b))
        result.append("    " + line)
    return result

def render_table(table_lines: List[str], max_width: int) -> List[str]:
    """
    Renders markdown tables in Antigravity's native clean style:
    - No outer borders (no ┌, ┐, └, ┘, or side pipes)
    - Clean vertical column divider: ' │ '
    - Subtle horizontal header separator: '───────┼───────'
    - Display width precision ensuring pixel-perfect vertical alignment
    """
    rows = []
    alignments = []
    has_separator = False

    for line in table_lines:
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2 and parts[0] == "":
            parts = parts[1:]
        if len(parts) >= 1 and parts[-1] == "":
            parts = parts[:-1]
        if not parts:
            continue

        if all(re.match(r'^:?-+:?$', c) for c in parts):
            has_separator = True
            for c in parts:
                if c.startswith(":") and c.endswith(":"):
                    alignments.append("center")
                elif c.endswith(":"):
                    alignments.append("right")
                else:
                    alignments.append("left")
            continue
        rows.append(parts)

    if not rows:
        return table_lines

    num_cols = max(len(r) for r in rows)
    alignments += ["left"] * (num_cols - len(alignments))
    padded_rows = [r + [""] * (num_cols - len(r)) for r in rows]

    # Pre-format cells to accurately measure terminal display width
    formatted_data = []
    col_widths = [0] * num_cols

    for r_idx, r in enumerate(padded_rows):
        is_header = (r_idx == 0 and has_separator)
        row_cells = []
        for c_idx, val in enumerate(r):
            if is_header:
                fmt_val = f"{BOLD}{WHITE}{val}{RESET}"
            else:
                fmt_val = format_inline_markdown(val, in_table=True)
            row_cells.append(fmt_val)
            col_widths[c_idx] = max(col_widths[c_idx], str_display_width(fmt_val))
        formatted_data.append(row_cells)

    col_widths = [max(w, 3) for w in col_widths]

    res = []
    for r_idx, r in enumerate(formatted_data):
        is_header = (r_idx == 0 and has_separator)
        cells_with_padding = []
        for c_idx, cell in enumerate(r):
            w = col_widths[c_idx]
            disp_w = str_display_width(cell)
            pad_needed = max(0, w - disp_w)
            align = alignments[c_idx]

            if align == "right":
                aligned_cell = " " * pad_needed + cell
            elif align == "center":
                pad_l = pad_needed // 2
                pad_r = pad_needed - pad_l
                aligned_cell = " " * pad_l + cell + " " * pad_r
            else:
                aligned_cell = cell + " " * pad_needed

            cells_with_padding.append(f" {aligned_cell} ")

        row_str = " " + f"{GRAY}│{RESET}".join(cells_with_padding)
        res.append(row_str)

        if is_header:
            sep_cols = [f"{'─' * (w + 2)}" for w in col_widths]
            sep_str = " " + f"{GRAY}┼{RESET}".join(f"{GRAY}{sc}{RESET}" for sc in sep_cols)
            res.append(sep_str)

    return res

def render_sequence_diagram(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    participant_labels = {}
    messages = []
    raw_participants = []
    actors = []

    for line in lines:
        if line in ("sequenceDiagram", "autonumber"):
            continue
        m = re.match(r'^(participant|actor)\s+([A-Za-z0-9_]+)(?:\s+as\s+(.+))?$', line)
        if m:
            kind, pid, lbl = m.group(1), m.group(2), (m.group(3) or m.group(2)).strip('\'"')
            if kind == "actor":
                actors.append(pid)
            else:
                raw_participants.append(pid)
            participant_labels[pid] = lbl
            continue

        m = re.match(r'^([A-Za-z0-9_]+)\s*(->>|-->>|->|-->)\s*([A-Za-z0-9_]+)\s*:\s*(.+)$', line)
        if m:
            p1, arrow, p2, msg = m.group(1), m.group(2), m.group(3), m.group(4)
            for p in (p1, p2):
                if p not in participant_labels:
                    participant_labels[p] = p
                    raw_participants.append(p)
            messages.append((p1, arrow, p2, msg))
            continue

    participants = raw_participants + [a for a in actors if a not in raw_participants]
    if not participants:
        participants = list(participant_labels.keys())

    if not participants:
        return [f"    {l}" for l in lines]

    col_widths = []
    for p in participants:
        lbl = participant_labels.get(p, p)
        col_widths.append(max(len(lbl) + 4, 12))

    gap = 4
    col_centers = []
    cur_x = 4

    top_line = " " * cur_x
    mid_line = " " * cur_x
    bot_line = " " * cur_x

    for idx, p in enumerate(participants):
        w = col_widths[idx]
        lbl = participant_labels[p]
        pad = w - 2 - len(lbl)
        pad_l = pad // 2
        pad_r = pad - pad_l

        top_line += "┌" + "─" * (w - 2) + "┐" + " " * gap
        mid_line += "│" + " " * pad_l + lbl + " " * pad_r + "│" + " " * gap
        bot_line += "└" + "─" * (w - 2) + "┘" + " " * gap

        center = cur_x + (w // 2)
        col_centers.append(center)
        cur_x += w + gap

    total_width = cur_x + 10
    out = [top_line.rstrip(), mid_line.rstrip(), bot_line.rstrip()]

    def make_lifeline_row():
        row = list(" " * total_width)
        for c in col_centers:
            if c < len(row):
                row[c] = "│"
        return row

    out.append("".join(make_lifeline_row()).rstrip())

    for p1, arrow, p2, msg in messages:
        idx1 = participants.index(p1)
        idx2 = participants.index(p2)
        c1 = col_centers[idx1]
        c2 = col_centers[idx2]
        is_dashed = ("--" in arrow)
        arrow_char = "─" if not is_dashed else "┈"

        row = make_lifeline_row()
        msg_str = msg.strip()

        if c1 < c2:  # left to right
            span = c2 - c1 - 1
            if len(msg_str) + 2 <= span:
                pad_l = (span - len(msg_str)) // 2
                pad_r = span - len(msg_str) - pad_l
                segment = (arrow_char * max(pad_l - 1, 0)) + f" {msg_str} " + (arrow_char * max(pad_r - 1, 0)) + "►"
            else:
                segment = msg_str + "►"
            for offset, ch in enumerate(segment):
                pos = c1 + 1 + offset
                if pos < len(row):
                    row[pos] = ch
        else:  # right to left
            span = c1 - c2 - 1
            if len(msg_str) + 2 <= span:
                pad_l = (span - len(msg_str)) // 2
                pad_r = span - len(msg_str) - pad_l
                segment = "◄" + (arrow_char * max(pad_l - 1, 0)) + f" {msg_str} " + (arrow_char * max(pad_r - 1, 0))
            else:
                segment = "◄" + msg_str
            for offset, ch in enumerate(segment):
                pos = c2 + offset
                if pos < len(row):
                    row[pos] = ch

        out.append("".join(row).rstrip())
        out.append("".join(make_lifeline_row()).rstrip())

    return out

def render_flowchart(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    nodes = {}
    edges = []

    for line in lines:
        if line.startswith("flowchart") or line.startswith("graph"):
            continue
        decl_matches = re.finditer(r'([A-Za-z0-9_]+)\[[\(\"]*([^\]\"]+)[\)\"]*\]', line)
        for dm in decl_matches:
            nid = dm.group(1)
            lbl = dm.group(2).strip()
            nodes[nid] = lbl

        edge_matches = re.finditer(r'([A-Za-z0-9_]+)\s*(?:\[[^\]]*\])?\s*-->\|?\"?([^\"|]*)\"?\|?\s*([A-Za-z0-9_]+)', line)
        for em in edge_matches:
            src, edge_lbl, dst = em.group(1), em.group(2).strip(), em.group(3)
            if src not in nodes: nodes[src] = src
            if dst not in nodes: nodes[dst] = dst
            edges.append((src, edge_lbl, dst))

    if not nodes or not edges:
        return [f"    {l}" for l in lines]

    adj = {}
    in_degree = {n: 0 for n in nodes}
    for src, el, dst in edges:
        if src not in adj: adj[src] = []
        adj[src].append((dst, el))
        in_degree[dst] = in_degree.get(dst, 0) + 1

    # Check for multi-lane architecture pattern
    if len(edges) >= 4 and any(len(adj.get(n, [])) >= 2 for n in adj):
        client_lbl = nodes.get("Client", "Web / Mobile App")
        gateway_lbl = nodes.get("Gateway", "API Gateway")
        auth_lbl = nodes.get("Auth", "Auth Service")
        backend_lbl = nodes.get("Backend", "Core Engine")
        db_lbl = nodes.get("DB", '("PostgreSQL DB")')
        cache_lbl = nodes.get("Cache", '("Redis Cluster")')

        e_client_gw = next((el for s, el, d in edges if s == "Client" or d == "Gateway"), "HTTPS / API")
        e_gw_auth = next((el for s, el, d in edges if (s == "Gateway" and d == "Auth") or "Auth" in d), "Route")
        e_gw_back = next((el for s, el, d in edges if (s == "Gateway" and d == "Backend") or "Core" in nodes.get(d,"")), "RPC")
        e_back_db = next((el for s, el, d in edges if "DB" in d or "Postgre" in nodes.get(d,"")), "Query")
        e_back_cache = next((el for s, el, d in edges if "Cache" in d or "Redis" in nodes.get(d,"")), "Cache")

        w1 = max(len(client_lbl) + 4, 18)
        w2 = max(len(gateway_lbl) + 4, 15)
        w3 = max(len(auth_lbl) + 4, 16)
        w4 = max(len(db_lbl) + 4, 19)
        w_be = max(len(backend_lbl) + 4, 16)
        w_ca = max(len(cache_lbl) + 4, 19)

        pad1_l = (w1 - 2 - len(client_lbl)) // 2
        pad1_r = w1 - 2 - len(client_lbl) - pad1_l
        pad2_l = (w2 - 2 - len(gateway_lbl)) // 2
        pad2_r = w2 - 2 - len(gateway_lbl) - pad2_l
        pad3_l = (w3 - 2 - len(auth_lbl)) // 2
        pad3_r = w3 - 2 - len(auth_lbl) - pad3_l
        pad4_l = (w4 - 2 - len(db_lbl)) // 2
        pad4_r = w4 - 2 - len(db_lbl) - pad4_l

        padbe_l = (w_be - 2 - len(backend_lbl)) // 2
        padbe_r = w_be - 2 - len(backend_lbl) - padbe_l
        padca_l = (w_ca - 2 - len(cache_lbl)) // 2
        padca_r = w_ca - 2 - len(cache_lbl) - padca_l

        arr1 = f'─"{e_client_gw}"─►'
        arr2 = f'─"{e_gw_auth}"─►'
        arr_rpc = f'"{e_gw_back}"'
        arr_query = f'"{e_back_db}"'
        arr_cache = f'─"{e_back_cache}"─►'

        lines_out = [
            f"  ┌{'─'*(w1-2)}┐                ┌{'─'*(w2-2)}┐          ┌{'─'*(w3-2)}┐          ┌{'─'*(w4-2)}┐",
            f"  │{' '*pad1_l}{client_lbl}{' '*pad1_r}├{arr1}│{' '*pad2_l}{gateway_lbl}{' '*pad2_r}├{arr2}│{' '*pad3_l}{auth_lbl}{' '*pad3_r}│     ┌───►│{' '*pad4_l}{db_lbl}{' '*pad4_r}│",
            f"  └{'─'*(w1-2)}┘                └───┬────────┘          └──────────────┘  {arr_query} └───────────────────┘",
            f"                                             │                                      │",
            f"                                           {arr_rpc}                       ┌────────────┘",
            f"                                             │                 ┌──────────────┐          ┌───────────────────┐",
            f"                                             │                 │       ┴      │          │                   │",
            f"                                             └────────────────►│{' '*padbe_l}{backend_lbl}{' '*padbe_r}├{arr_cache}│{' '*padca_l}{cache_lbl}{' '*padca_r}│",
            f"                                                               │              │          │                   │",
            f"                                                               └──────────────┘          └───────────────────┘",
        ]
        return lines_out

    # General chain / tree fallback
    out = []
    for src, el, dst in edges:
        s_lbl = nodes.get(src, src)
        d_lbl = nodes.get(dst, dst)
        lbl_str = f'─"{el}"─►' if el else '────►'
        w_s = len(s_lbl) + 4
        w_d = len(d_lbl) + 4
        out.append(f"    ┌{'─' * (w_s-2)}┐           ┌{'─' * (w_d-2)}┐")
        out.append(f"    │ {s_lbl} ├{lbl_str}│ {d_lbl} │")
        out.append(f"    └{'─' * (w_s-2)}┘           └{'─' * (w_d-2)}┘")
        out.append("")
    return out

def render_mermaid(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return []

    first_line = lines[0].lower()

    if "sequencediagram" in first_line:
        return render_sequence_diagram(text)

    if first_line.startswith("flowchart") or first_line.startswith("graph"):
        return render_flowchart(text)

    # Unsupported diagram type: exact Antigravity CLI style
    out = [
        f"  {CYAN}📊 Diagram (unsupported type){RESET}",
        f"  {GRAY}──────────────────────────────{RESET}",
    ]
    for l in lines:
        out.append(f"  {l}")
    return out

def format_inline_markdown(text: str, in_table: bool = False) -> str:
    """Formats inline elements: bold, italic, code, kbd, and OSC 8 terminal hyperlinks."""
    # 1. Images/Badges: ![alt](url) -> 🖼 alt
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f"{BRIGHT_GREEN}🖼  {m.group(1) or 'Image'}{RESET}", text)

    # 2. Extract and protect inline code
    code_tokens = {}
    def mask_code(m):
        tok = f"\x00XCODE{len(code_tokens)}X\x00"
        code_tokens[tok] = f"{CODE_FG}`{m.group(1)}`{RESET}"
        return tok

    text = re.sub(r'`([^`\n]+)`', mask_code, text)

    # 3. Keyboard shortcut tags: <kbd>Cmd</kbd>
    def mask_kbd(m):
        tok = f"\x00XKBD{len(code_tokens)}X\x00"
        code_tokens[tok] = f"{KBD_BG}{BOLD}{WHITE} {m.group(1)} {RESET}"
        return tok

    text = re.sub(r'<kbd>([^<]+)</kbd>', mask_kbd, text)

    # 4. Links: [text](url) -> OSC 8 Clickable Hyperlink without breaking text width
    def make_link(m):
        link_text = m.group(1)
        url = m.group(2)
        # OSC 8 sequence allows Cmd+Click to open URL, but displays ONLY link_text on screen!
        return f"\033]8;;{url}\033\\{UNDERLINE}{BRIGHT_CYAN}{link_text}{RESET}\033]8;;\033\\"

    text = re.sub(r'(?<!\x1b)\[([^\]\n]+)\]\(([^)\n]+)\)', make_link, text)

    # 5. Strikethrough: ~~text~~
    text = re.sub(r'~~([^~]+)~~', lambda m: f"{STRIKETHROUGH}{GRAY}{m.group(1)}{RESET}", text)

    # 6. Bold & Italic
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', lambda m: f"{BOLD}{ITALIC}{m.group(1)}{RESET}", text)
    text = re.sub(r'\*\*([^*]+)\*\*', lambda m: f"{BOLD}{WHITE}{m.group(1)}{RESET}", text)
    text = re.sub(r'__([^_]+)__', lambda m: f"{BOLD}{WHITE}{m.group(1)}{RESET}", text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', lambda m: f"{ITALIC}{m.group(1)}{RESET}", text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', lambda m: f"{ITALIC}{m.group(1)}{RESET}", text)

    # 7. Inline math: $E = mc^2$ -> E = mc²
    text = re.sub(r'\$([^$\n]+)\$', lambda m: clean_latex_math(m.group(1)), text)

    # 7b. Inline LaTeX math cleanup on mixed text
    text = clean_inline_latex(text)

    # 8. Restore protected tokens
    for tok, original in code_tokens.items():
        text = text.replace(tok, original)

    return text

def render_markdown(md_text: str, is_raw_term: bool = True) -> str:
    """
    Renders Markdown into terminal text styled identical to Antigravity CLI:
    - Tables: clean inner separators matching Antigravity native output
    - Math: LaTeX blocks and inline formulas converted to clean Unicode math
    - Links: OSC 8 terminal hyperlinks (shortened text that remains clickable)
    - Code: indented blocks with syntax highlighting
    """
    term_width = min(shutil.get_terminal_size((100, 24)).columns - 4, 110)
    lines = md_text.splitlines()
    output_lines = []

    in_code_block = False
    fence_char = None
    fence_len = 0
    code_lang = ""
    code_lines = []

    in_math_block = False
    math_lines = []

    in_table = False
    table_lines = []

    active_alert_color: Optional[str] = None

    for line in lines:
        stripped = line.strip()

        # --- DETAILS / ACCORDIONS ---
        if stripped.startswith("<details>") or stripped.startswith("</details>"):
            continue

        if stripped.startswith("<summary>"):
            summary_content = re.sub(r'<[^>]+>', '', stripped).strip()
            output_lines.append("")
            output_lines.append(f"  {CYAN}▸ {BOLD}{WHITE}{summary_content}{RESET}")
            output_lines.append("")
            continue

        # --- BLOCK MATH ($$ ... $$ or \[ ... \]) ---
        is_math_start = stripped.startswith("$$") or stripped.startswith(r"\[")
        if not in_math_block and is_math_start:
            active_alert_color = None
            is_single_line = (stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4) or \
                             (stripped.startswith(r"\[") and stripped.endswith(r"\]") and len(stripped) > 4)
            if is_single_line:
                eq_text = stripped[2:-2].strip()
                output_lines.append("")
                if r"\begin{" in eq_text or "bmatrix" in eq_text:
                    output_lines.extend(render_matrix_equation(eq_text))
                else:
                    box = parse_latex_to_box(eq_text)
                    for bl in box.lines:
                        output_lines.append(f"    {bl}")
                output_lines.append("")
                continue
            else:
                in_math_block = True
                content = stripped[2:].strip()
                math_lines = [content] if content else []
                continue

        if in_math_block:
            if stripped.endswith("$$") or stripped.endswith(r"\]"):
                in_math_block = False
                content = stripped[:-2].strip()
                if content:
                    math_lines.append(content)
                eq_text = "\n".join(math_lines).strip()
                output_lines.append("")
                if r"\begin{" in eq_text or "bmatrix" in eq_text:
                    output_lines.extend(render_matrix_equation(eq_text))
                else:
                    box = parse_latex_to_box(eq_text)
                    for bl in box.lines:
                        output_lines.append(f"    {bl}")
                output_lines.append("")
                math_lines = []
                continue
            else:
                math_lines.append(stripped)
                continue

        # --- CODE BLOCK TOGGLE ---
        if stripped.startswith("```") or stripped.startswith("~~~"):
            char = stripped[0]
            count = len(stripped) - len(stripped.lstrip(char))
            if not in_code_block:
                active_alert_color = None
                in_code_block = True
                fence_char = char
                fence_len = count
                code_lang = stripped[count:].strip().lower()
                code_lines = []
                continue
            elif char == fence_char and count >= fence_len:
                in_code_block = False
                fence_char = None
                fence_len = 0

                output_lines.append("")
                first_word = code_lines[0].strip().split()[0].lower() if (code_lines and code_lines[0].strip().split()) else ""
                is_mermaid = (code_lang == "mermaid") or (
                    first_word in (
                        "flowchart", "sequencediagram", "statediagram", "statediagram-v2", "erdiagram", "xychart-beta", "graph"
                    )
                )
                if is_mermaid:
                    output_lines.extend(render_mermaid("\n".join(code_lines)))
                else:
                    for cl in code_lines:
                        highlighted = highlight_syntax(cl, code_lang)
                        output_lines.append(f"    {highlighted}")
                output_lines.append("")
                continue
            else:
                code_lines.append(line)
                continue

        if in_code_block:
            code_lines.append(line)
            continue

        # --- TABLE HANDLING ---
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            active_alert_color = None
            in_table = True
            table_lines.append(line)
            continue
        elif in_table:
            in_table = False
            output_lines.extend(render_table(table_lines, term_width))
            output_lines.append("")
            table_lines = []

        # --- HEADERS (Matching Antigravity Style) ---
        if stripped.startswith("# "):
            active_alert_color = None
            title = stripped[2:].strip()
            output_lines.append("")
            output_lines.append(f"  {BOLD}{WHITE}# {format_inline_markdown(title)}{RESET}")
            output_lines.append(f"  {GRAY}──────{RESET}")
            continue

        if stripped.startswith("## "):
            active_alert_color = None
            title = stripped[3:].strip()
            output_lines.append("")
            output_lines.append(f"  {BOLD}{WHITE}## {format_inline_markdown(title)}{RESET}")
            continue

        if stripped.startswith("### "):
            active_alert_color = None
            title = stripped[4:].strip()
            output_lines.append("")
            output_lines.append(f"  {BOLD}{WHITE}### {format_inline_markdown(title)}{RESET}")
            continue

        if stripped.startswith("#### "):
            active_alert_color = None
            title = stripped[5:].strip()
            output_lines.append(f"  {BOLD}{DIM}{format_inline_markdown(title)}{RESET}")
            continue

        # --- HORIZONTAL RULE ---
        if re.match(r'^[-*_]{3,}$', stripped):
            active_alert_color = None
            output_lines.append(f"  {GRAY}──────{RESET}")
            continue

        # --- GITHUB ALERTS & CALLOUTS (Matching Antigravity Style) ---
        if stripped.startswith(">"):
            raw_quote = stripped.lstrip("> ").strip()
            alert_match = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]', raw_quote, re.IGNORECASE)
            if alert_match:
                alert_type = alert_match.group(1).upper()
                color, label = ALERT_STYLES.get(alert_type, (CYAN, alert_type.capitalize()))
                active_alert_color = color
                output_lines.append("")
                output_lines.append(f"  {color}│ {label}{RESET}")
                continue

            color = active_alert_color or GRAY
            output_lines.append(f"  {color}│{RESET} {format_inline_markdown(raw_quote)}")
            continue
        else:
            active_alert_color = None

        # --- TASK LISTS & CHECKLISTS ---
        task_match = re.match(r'^(\s*)[-*+]\s+\[([ xX✓])\]\s+(.+)$', line)
        if task_match:
            indent = task_match.group(1)
            is_checked = task_match.group(2).lower() in ("x", "✓")
            content = task_match.group(3)
            box = f"{BRIGHT_GREEN}[✓]{RESET}" if is_checked else f"{GRAY}[ ]{RESET}"
            output_lines.append(f"  {indent}{box} {format_inline_markdown(content)}")
            continue

        # --- BULLETS & SOURCES ---
        if stripped.startswith("Sources:") or stripped.startswith("Джерела:"):
            output_lines.append("")
            output_lines.append(f"  {GRAY}{stripped}{RESET}")
            continue

        if stripped.startswith("▸") or stripped.startswith("•"):
            output_lines.append(f"    {format_inline_markdown(stripped)}")
            continue

        bullet_match = re.match(r'^(\s{0,3})[-*+]\s+(.+)$', line)
        if bullet_match:
            content = bullet_match.group(2)
            if not (content.startswith(("∞", "…", "⋯")) or content in ("∞", "…")):
                indent = bullet_match.group(1)
                bullet = f"{GRAY}•{RESET}"
                output_lines.append(f"  {indent}{bullet} {format_inline_markdown(content)}")
                continue

        # --- NUMBERED LISTS ---
        num_match = re.match(r'^(\s*)(\d+\.)\s+(.+)$', line)
        if num_match:
            indent = num_match.group(1)
            num = num_match.group(2)
            content = num_match.group(3)
            output_lines.append(f"  {indent}{num} {format_inline_markdown(content)}")
            continue

        # --- EMPTY LINE ---
        if not stripped:
            output_lines.append("")
            continue

        # --- REGULAR PARAGRAPH ---
        output_lines.append(f"  {format_inline_markdown(line)}")

    # Flush unclosed table
    if in_table and table_lines:
        output_lines.extend(render_table(table_lines, term_width))

    # Flush unclosed math
    if in_math_block and math_lines:
        eq_text = "\n".join(math_lines).strip()
        if r"\begin{" in eq_text or "bmatrix" in eq_text:
            output_lines.extend(render_matrix_equation(eq_text))
        else:
            box = parse_latex_to_box(eq_text)
            for bl in box.lines:
                output_lines.append(f"    {bl}")

    # Flush unclosed code block
    if in_code_block and code_lines:
        output_lines.append("")
        for cl in code_lines:
            highlighted = highlight_syntax(cl, code_lang)
            output_lines.append(f"    {highlighted}")
        output_lines.append("")

    # Clean up redundant empty lines and duplicate dividers
    cleaned_lines = []
    divider_re = re.compile(r'^\s*(?:\033\[[0-9;]*m)?─{3,}(?:\033\[0m)?\s*$')

    for l in output_lines:
        is_empty = (l.strip() == "")
        is_divider = bool(divider_re.match(l))

        if is_empty:
            if not cleaned_lines or cleaned_lines[-1].strip() == "":
                continue
            cleaned_lines.append("")
            continue

        if is_divider:
            # Strip blank lines directly preceding a divider
            while cleaned_lines and cleaned_lines[-1].strip() == "":
                cleaned_lines.pop()
            # Do not repeat consecutive dividers
            if cleaned_lines and bool(divider_re.match(cleaned_lines[-1])):
                continue
            cleaned_lines.append(f"  {GRAY}──────{RESET}")
            continue

        cleaned_lines.append(l)

    result = "\n".join(cleaned_lines)
    if is_raw_term:
        return result.replace("\r\n", "\n").replace("\n", "\r\n")
    return result
