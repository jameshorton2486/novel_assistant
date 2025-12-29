"""
GUI Module
==========

PyQt6 interfaces for Novel Assistant.

Requires: pip install PyQt6
"""

try:
    from .research_intake import (
        ResearchIntakeWindow,
        launch_intake_gui,
        cli_intake
    )
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    
    def launch_intake_gui(*args, **kwargs):
        print("PyQt6 not installed. Run: pip install PyQt6")
        return None
    
    def cli_intake(*args, **kwargs):
        print("CLI intake mode.")

__all__ = [
    'launch_intake_gui',
    'cli_intake',
    'GUI_AVAILABLE'
]
