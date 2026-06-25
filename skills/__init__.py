"""Skills package — auto-discovers and registers every domain module.

To add a new skill domain:
  1. Create  skills/<domain_name>.py
  2. Define your async skill functions inside it
  3. Add a  register_all()  function that calls
       get_registry().register("<agent_type>", "<skill_name>", fn, schema)
     for each skill.
  4. Done — no other files need to change.

Any .py file in this directory that is not __init__.py and exposes a
callable register_all() will be loaded automatically on startup.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import List

import structlog

logger = structlog.get_logger()

_SKIP = {"__init__"}


def _discover_domain_modules() -> List[str]:
    pkg_path = str(Path(__file__).parent)
    return [
        name
        for _finder, name, _ispkg in pkgutil.iter_modules([pkg_path])
        if name not in _SKIP
    ]


def register_all() -> None:
    domains = _discover_domain_modules()
    loaded, skipped = [], []

    for name in domains:
        full_name = f"skills.{name}"
        try:
            mod = importlib.import_module(full_name)
            if callable(getattr(mod, "register_all", None)):
                mod.register_all()
                loaded.append(name)
            else:
                skipped.append(f"{name} (no register_all)")
        except Exception as exc:
            skipped.append(f"{name} ({exc})")
            logger.warning("Skill domain failed to load", domain=name, error=str(exc))

    logger.info("Skills loaded", loaded=loaded, skipped=skipped)
