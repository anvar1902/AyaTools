from importlib import import_module
from pkgutil import iter_modules
from inspect import isclass
from pathlib import Path

ALL_COMMANDS = {}   # {"command": <class '...Command'>, ...}

_package_dir = Path(__file__).parent

# Собираем имена модулей (только .py, без подпакетов и скрытых)
_module_names = sorted(
    name
    for _, name, is_pkg in iter_modules([str(_package_dir)])
    if not is_pkg and not name.startswith("_")
)

for _name in _module_names:
    _mod = import_module(f"{__name__}.{_name}")
    _cls = getattr(_mod, "Command", None)
    if isclass(_cls):
        ALL_COMMANDS[_cls.command] = _cls

__all__ = ["ALL_COMMANDS"]
