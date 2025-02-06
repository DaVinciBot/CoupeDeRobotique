# ====== Code Summary ======
# This module defines different color schemes for log levels using the `colorama` library.
# It provides a base class (`BaseColors`) and multiple subclasses (`ClassicColors`, `DarkModeColors`, etc.)
# that define color mappings for log levels such as DEBUG, INFO, WARNING, ERROR, CRITICAL, and FATAL.
# These classes can be used to format log messages with different visual styles.

# Base class for colors
from logger.colors.base import BaseColors

# Derived color classes
from logger.colors.classic import ClassicColors
from logger.colors.cyberpunk import CyberpunkColors
from logger.colors.dark_mode import DarkModeColors
from logger.colors.neon import NeonColors
from logger.colors.pastel import PastelColors
