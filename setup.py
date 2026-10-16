from setuptools import setup, find_packages

setup(
    name="shpak",
    version="3.0.0",
    description="Zero-token transparent PTY wrapper and prompt translator for AI agents (Antigravity, Claude, Codex, Cursor)",
    author="Sergey Pylypyshko",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "spk=shpak.cli:main",
            "shpak=shpak.cli:main",
            "agy-spk=shpak.wrapper:main",
            "agy-shpak=shpak.wrapper:main",
            "claude-spk=shpak.wrapper:main",
            "claude-shpak=shpak.wrapper:main",
            "codex-spk=shpak.wrapper:main",
            "codex-shpak=shpak.wrapper:main",
            "cursor-spk=shpak.wrapper:main",
            "cursor-shpak=shpak.wrapper:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.9",
)
