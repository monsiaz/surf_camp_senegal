"""Utility: load .env from project root if OPENAI_API_KEY is not already set."""

import os
from pathlib import Path


def load_dotenv_if_needed():
    """Load .env from the project root into os.environ (simple parser, no deps)."""
    if os.environ.get("OPENAI_API_KEY"):
        return  # already set

    # Walk up from this script's directory to find .env
    root = Path(__file__).parent.parent
    env_file = root / ".env"
    if not env_file.exists():
        return

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


# Auto-load on import
load_dotenv_if_needed()
