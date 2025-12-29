"""
Governance module - Canon management, versioning, and consistency checks.
"""

from .canon_manager import CanonManager, ChapterState
from .regression_checker import RegressionChecker

__all__ = ["CanonManager", "ChapterState", "RegressionChecker"]
