"""
Writing Mode Checklist - Pre-writing confirmation tool.

This is NOT a tutorial, NOT a feature-heavy workflow, and NOT AI-driven.
It is a lightweight, intentional gate that prepares the system and the author
for focused writing.

Design Intent:
- Fast (30-60 seconds to complete)
- Human-affirming, not AI-led
- Explicitly minimizes distraction
- Protects canon and research discipline
- Encourages momentum, not perfection
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QTextEdit, QPushButton, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from governance.canon_manager import CanonManager, ChapterState

logger = logging.getLogger(__name__)


class WritingModeDialog(QDialog):
    """
    Writing Mode checklist dialog.
    
    This checklist is a PRE-WRITING confirmation tool only.
    It exists to protect focus and discipline, not to add intelligence.
    """
    
    def __init__(self, parent, canon_manager: Optional[CanonManager] = None,
                 current_chapter: Optional[str] = None):
        super().__init__(parent)
        
        self.canon_manager = canon_manager
        self.current_chapter = current_chapter
        self.confirmed = False
        
        self.setWindowTitle("Enter Writing Mode")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self._build_ui()
        self._populate_data()
        
        logger.info("Writing Mode dialog opened")
    
    def _build_ui(self) -> None:
        """Build the checklist UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Writing Mode Checklist")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # 1. PROJECT STATE CONFIRMATION
        project_group = QGroupBox("1. Project State")
        project_layout = QVBoxLayout()
        
        self.project_label = QLabel("Active Project: [Loading...]")
        project_layout.addWidget(self.project_label)
        
        self.chapter_label = QLabel("Active Chapter: [None]")
        project_layout.addWidget(self.chapter_label)
        
        self.status_label = QLabel("Chapter Status: [Unknown]")
        project_layout.addWidget(self.status_label)
        
        self.status_warning = QLabel("")
        self.status_warning.setWordWrap(True)
        self.status_warning.setStyleSheet("color: #d32f2f; font-weight: bold;")
        project_layout.addWidget(self.status_warning)
        
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # 2. CANON & CONTEXT AWARENESS
        canon_group = QGroupBox("2. Canon & Context Awareness")
        canon_layout = QVBoxLayout()
        
        self.canon_version_label = QLabel("Canon Version: [Loading...]")
        canon_layout.addWidget(self.canon_version_label)
        
        self.canon_date_label = QLabel("Last Canon Change: [Unknown]")
        canon_layout.addWidget(self.canon_date_label)
        
        self.canon_checkbox = QCheckBox("I am writing within established canon")
        canon_layout.addWidget(self.canon_checkbox)
        
        canon_group.setLayout(canon_layout)
        layout.addWidget(canon_group)
        
        # 3. RESEARCH DISCIPLINE
        research_group = QGroupBox("3. Research Discipline")
        research_layout = QVBoxLayout()
        
        self.research_label = QLabel("Active References: [Loading...]")
        research_layout.addWidget(self.research_label)
        
        self.research_checkbox = QCheckBox("I will mark placeholders instead of researching")
        research_layout.addWidget(self.research_checkbox)
        
        research_group.setLayout(research_layout)
        layout.addWidget(research_group)
        
        # 4. STYLE & ERA GUARDRAILS
        style_group = QGroupBox("4. Style & Era Guardrails")
        style_layout = QVBoxLayout()
        
        self.style_label = QLabel("Style Charter: Active (1950s voice)")
        style_layout.addWidget(self.style_label)
        
        self.era_label = QLabel("Era Constraints: 1954, California, Circus")
        style_layout.addWidget(self.era_label)
        
        self.style_checkbox = QCheckBox("I will prioritize restraint and period accuracy")
        style_layout.addWidget(self.style_checkbox)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # 5. SESSION INTENT
        intent_group = QGroupBox("5. Session Intent (Optional)")
        intent_layout = QVBoxLayout()
        
        intent_hint = QLabel("What am I trying to accomplish this session?")
        intent_hint.setStyleSheet("color: #666; font-style: italic;")
        intent_layout.addWidget(intent_hint)
        
        self.intent_field = QTextEdit()
        self.intent_field.setPlaceholderText(
            "Examples:\n"
            "- Draft scene only\n"
            "- Fix pacing\n"
            "- Finish chapter section"
        )
        self.intent_field.setMaximumHeight(80)
        intent_layout.addWidget(self.intent_field)
        
        intent_group.setLayout(intent_layout)
        layout.addWidget(intent_group)
        
        # 6. EXIT CONDITIONS
        exit_group = QGroupBox("6. Exit Conditions (Optional)")
        exit_layout = QVBoxLayout()
        
        self.exit_checkbox = QCheckBox("Stop when momentum fades — do not over-revise")
        exit_layout.addWidget(self.exit_checkbox)
        
        exit_group.setLayout(exit_layout)
        layout.addWidget(exit_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        enter_btn = QPushButton("Enter Writing Mode")
        enter_btn.setDefault(True)
        enter_btn.setStyleSheet("font-weight: bold; padding: 5px 15px;")
        enter_btn.clicked.connect(self._on_enter_writing_mode)
        button_layout.addWidget(enter_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_data(self) -> None:
        """Populate checklist with current system state."""
        # Project state
        if self.current_chapter:
            self.chapter_label.setText(f"Active Chapter: {self.current_chapter}")
            
            # Get chapter state from canon manager
            if self.canon_manager:
                try:
                    state = self.canon_manager.get_chapter_state(self.current_chapter)
                    self.status_label.setText(f"Chapter Status: {state.value.title()}")
                    
                    # Warn if locked
                    if state == ChapterState.CANON_LOCKED:
                        self.status_warning.setText(
                            "⚠️ WARNING: This chapter is Canon-Locked. "
                            "Unlocking requires explicit reason."
                        )
                    elif state == ChapterState.PUBLISHED:
                        self.status_warning.setText(
                            "⚠️ WARNING: This chapter is Published (read-only)."
                        )
                except Exception as e:
                    logger.warning(f"Error getting chapter state: {e}")
                    self.status_label.setText("Chapter Status: Unknown")
        else:
            self.chapter_label.setText("Active Chapter: [None - create or open a chapter]")
            self.status_label.setText("Chapter Status: N/A")
        
        # Canon information
        if self.canon_manager:
            try:
                version_info = self.canon_manager.get_version_info()
                self.canon_version_label.setText(
                    f"Canon Version: {version_info.get('version', 'Unknown')}"
                )
                
                last_update = version_info.get('last_update')
                if last_update:
                    # Format date nicely
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                        formatted = dt.strftime("%Y-%m-%d %H:%M")
                        self.canon_date_label.setText(f"Last Canon Change: {formatted}")
                    except:
                        self.canon_date_label.setText(f"Last Canon Change: {last_update}")
                else:
                    self.canon_date_label.setText("Last Canon Change: Never")
            except Exception as e:
                logger.warning(f"Error getting canon info: {e}")
                self.canon_version_label.setText("Canon Version: [Error loading]")
        else:
            self.canon_version_label.setText("Canon Version: [Not available]")
            self.canon_date_label.setText("Last Canon Change: [Not available]")
        
        # Research references (simplified - just show that system is ready)
        self.research_label.setText("Active References: Canon, Context, Artifacts available")
    
    def _on_enter_writing_mode(self) -> None:
        """Handle Enter Writing Mode button click."""
        # Validate required checkboxes
        if not self.canon_checkbox.isChecked():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Confirmation Required",
                "Please confirm that you are writing within established canon."
            )
            return
        
        if not self.research_checkbox.isChecked():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Confirmation Required",
                "Please confirm your research discipline approach."
            )
            return
        
        if not self.style_checkbox.isChecked():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Confirmation Required",
                "Please confirm your commitment to period accuracy."
            )
            return
        
        # All checks passed
        self.confirmed = True
        self.accept()
        logger.info("Writing Mode entered - checklist confirmed")
    
    def get_session_intent(self) -> str:
        """Get the session intent text (optional)."""
        return self.intent_field.toPlainText().strip()
    
    def should_stop_on_momentum_fade(self) -> bool:
        """Check if user wants to stop when momentum fades."""
        return self.exit_checkbox.isChecked()

