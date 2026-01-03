"""
Lolipop - Utility and Dev tool

utility for installation, setup, development, organising and more
"""

# make the handlers, modules, commands etc available at package level
from lolipop import handlers  # noqa: F401
from lolipop import modules  # noqa: F401
from lolipop import commands  # noqa: F401

__all__ = ["handlers", "modules", "commands"]