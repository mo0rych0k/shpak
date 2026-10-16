import os
import json
import re
from pathlib import Path
from typing import Optional, Tuple

def _find_antigravity_response(since_time: Optional[float] = None) -> Tuple[float, str]:
    """Extracts latest assistant response from Antigravity CLI and IDE session logs."""
    cli_brain = Path.home() / ".gemini" / "antigravity-cli" / "brain"
    ide_brain = Path.home() / ".gemini" / "antigravity-ide" / "brain"

    candidates = []
    for brain_dir in [cli_brain, ide_brain]:
        if not brain_dir.exists():
            continue
        for log_dir in brain_dir.glob("*/.system_generated/logs"):
            full_file = log_dir / "transcript_full.jsonl"
            regular_file = log_dir / "transcript.jsonl"
            chosen = full_file if full_file.exists() else regular_file
            if chosen.exists():
                try:
                    mtime = chosen.stat().st_mtime
                    if since_time is None or mtime >= (since_time - 10.0):
                        candidates.append((mtime, chosen))
                except OSError:
                    continue

    if not candidates and since_time is not None:
        for brain_dir in [cli_brain, ide_brain]:
            if not brain_dir.exists():
                continue
            for log_dir in brain_dir.glob("*/.system_generated/logs"):
                full_file = log_dir / "transcript_full.jsonl"
                regular_file = log_dir / "transcript.jsonl"
                chosen = full_file if full_file.exists() else regular_file
                if chosen.exists():
                    try:
                        candidates.append((chosen.stat().st_mtime, chosen))
                    except OSError:
                        continue

    if not candidates:
        return 0.0, ""

    candidates.sort(key=lambda x: x[0], reverse=True)

    for mtime, transcript_path in candidates:
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                first_lines = [f.readline() for _ in range(5)]
            header_text = "".join(first_lines)
            if "You are an expert technical translator" in header_text or "NON-NEGOTIABLE TRANSLATION RULES" in header_text:
                continue
        except Exception:
            continue

        last_resp = ""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("source") == "MODEL" and data.get("type") == "PLANNER_RESPONSE":
                            content = data.get("content")
                            if content and content.strip():
                                last_resp = content.strip()
                    except Exception:
                        continue
        except Exception:
            continue

        if last_resp:
            cleaned = re.sub(r'```json\s*\{\s*"session_status":[\s\S]*?\}\s*```', '', last_resp).strip()
            return mtime, (cleaned or last_resp)

    return 0.0, ""

def _find_claude_response(since_time: Optional[float] = None) -> Tuple[float, str]:
    """Extracts latest assistant response from Claude Code CLI session files."""
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        return 0.0, ""

    candidates = []
    for search_dir in [claude_dir / "projects", claude_dir / "sessions"]:
        if not search_dir.exists():
            continue
        for p in search_dir.rglob("*.jsonl"):
            try:
                mtime = p.stat().st_mtime
                if since_time is None or mtime >= (since_time - 10.0):
                    candidates.append((mtime, p))
            except OSError:
                continue

    if not candidates and since_time is not None:
        for search_dir in [claude_dir / "projects", claude_dir / "sessions"]:
            if not search_dir.exists():
                continue
            for p in search_dir.rglob("*.jsonl"):
                try:
                    candidates.append((p.stat().st_mtime, p))
                except OSError:
                    continue

    if not candidates:
        return 0.0, ""

    candidates.sort(key=lambda x: x[0], reverse=True)

    for mtime, transcript_path in candidates:
        last_resp = ""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("type") == "assistant" or data.get("role") == "assistant":
                            msg = data.get("message") if isinstance(data.get("message"), dict) else data
                            content = msg.get("content")
                            if isinstance(content, list):
                                texts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
                                joined = "\n".join([t for t in texts if t.strip()]).strip()
                                if joined:
                                    last_resp = joined
                            elif isinstance(content, str) and content.strip():
                                last_resp = content.strip()
                    except Exception:
                        continue
        except Exception:
            continue

        if last_resp:
            return mtime, last_resp

    return 0.0, ""

def _find_codex_response(since_time: Optional[float] = None) -> Tuple[float, str]:
    """Extracts latest assistant response from OpenAI Codex CLI session files."""
    codex_dir = Path.home() / ".codex" / "sessions"
    if not codex_dir.exists():
        return 0.0, ""

    candidates = []
    for p in codex_dir.rglob("*.jsonl"):
        try:
            mtime = p.stat().st_mtime
            if since_time is None or mtime >= (since_time - 10.0):
                candidates.append((mtime, p))
        except OSError:
            continue

    if not candidates and since_time is not None:
        for p in codex_dir.rglob("*.jsonl"):
            try:
                candidates.append((p.stat().st_mtime, p))
            except OSError:
                continue

    if not candidates:
        return 0.0, ""

    candidates.sort(key=lambda x: x[0], reverse=True)

    for mtime, transcript_path in candidates:
        last_resp = ""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        payload = data.get("payload")
                        if isinstance(payload, dict) and payload.get("role") == "assistant":
                            content = payload.get("content")
                            if isinstance(content, list):
                                texts = []
                                for b in content:
                                    if isinstance(b, dict):
                                        if b.get("type") in ("output_text", "text") or "text" in b:
                                            t = b.get("text", "").strip()
                                            if t:
                                                texts.append(t)
                                if texts:
                                    last_resp = "\n".join(texts).strip()
                            elif isinstance(content, str) and content.strip():
                                last_resp = content.strip()
                    except Exception:
                        continue
        except Exception:
            continue

        if last_resp:
            return mtime, last_resp

    return 0.0, ""

def _find_aider_response(since_time: Optional[float] = None) -> Tuple[float, str]:
    """Extracts latest assistant response from Aider CLI markdown chat history."""
    candidates = [
        Path.cwd() / ".aider.chat.history.md",
        Path.home() / ".aider.chat.history.md"
    ]
    for p in candidates:
        if p.exists():
            try:
                mtime = p.stat().st_mtime
                if since_time is None or mtime >= (since_time - 10.0):
                    with open(p, "r", encoding="utf-8") as f:
                        text = f.read()
                    parts = re.split(r'\n(?=#### |\n> )', text)
                    for part in reversed(parts):
                        lines = part.strip().splitlines()
                        if lines and not lines[0].startswith("> ") and not lines[0].startswith("#### "):
                            return mtime, part.strip()
            except Exception:
                continue
    return 0.0, ""

def _find_demo_response(since_time: Optional[float] = None) -> Tuple[float, str]:
    """Extracts response from interactive demo session."""
    import tempfile
    demo_file = Path(tempfile.gettempdir()) / "llm_tr_demo_session.txt"
    if demo_file.exists():
        try:
            mtime = demo_file.stat().st_mtime
            return mtime, demo_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return 0.0, ""

def get_latest_agent_response(target: Optional[str] = None, since_time: Optional[float] = None) -> str:
    """
    Finds and extracts the most recent clean Markdown response from:
    - Antigravity (target='agy' / 'antigravity')
    - Claude Code CLI (target='claude')
    - Codex CLI (target='codex')
    - Aider (target='aider')
    - Demo agent (target='demo' / 'test')
    - Or automatically from whichever CLI was updated most recently (target='auto' or None).
    """
    target_clean = (target or "").lower().strip()

    if target_clean in ("demo", "test"):
        _, resp = _find_demo_response(since_time=since_time)
        return resp

    if target_clean in ("claude", "claude-code", "claude-cli"):
        _, resp = _find_claude_response(since_time=since_time)
        return resp

    if target_clean in ("codex", "codex-cli"):
        _, resp = _find_codex_response(since_time=since_time)
        return resp

    if target_clean in ("antigravity", "agy", "ag"):
        _, resp = _find_antigravity_response(since_time=since_time)
        return resp

    if target_clean in ("aider",):
        _, resp = _find_aider_response(since_time=since_time)
        return resp

    # Target is "auto" or unknown: check all supported tools and pick the most recent
    candidates = [
        _find_demo_response(since_time=since_time),
        _find_antigravity_response(since_time=since_time),
        _find_claude_response(since_time=since_time),
        _find_codex_response(since_time=since_time),
        _find_aider_response(since_time=since_time)
    ]
    # Filter out empty responses and sort by mtime descending
    valid = [c for c in candidates if c[0] > 0 and c[1].strip()]
    if valid:
        valid.sort(key=lambda x: x[0], reverse=True)
        return valid[0][1]

    # Fallback retry without time constraint
    if since_time is not None:
        return get_latest_agent_response(target=target, since_time=None)

    return ""
