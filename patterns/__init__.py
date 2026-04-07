import importlib
import pkgutil
from patterns.base import Pattern

def discover() -> dict[str, type[Pattern]]:
    """Return {name: PatternClass} for every Pattern subclass in this package."""
    registry = {}
    for info in pkgutil.iter_modules(__path__):
        mod = importlib.import_module(f"{__name__}.{info.name}")
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, Pattern) and obj is not Pattern:
                registry[obj.NAME] = obj
    return registry
