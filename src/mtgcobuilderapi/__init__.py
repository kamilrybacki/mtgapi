"""
Backward compatibility shim for the old 'mtgcobuilderapi' package name.

This package re-exports public symbols from the new 'mtgapi' package so that
existing imports like `import mtgcobuilderapi.config.settings.api` continue to work.

The shim is temporary and will be removed in a future release. Update your imports to use 'mtgapi'.
"""
from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Package 'mtgcobuilderapi' is deprecated; use 'mtgapi' instead. This shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export by shallow import. If deeper submodules are needed, they will be loaded on demand.
from mtgapi import *  # noqa: F403
