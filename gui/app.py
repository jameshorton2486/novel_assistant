"""
Improved Novel Assistant Writing Studio with:
- AI Provider Toggle (OpenAI/Claude)
- Local File Save/Load
- Word Count Display
- Auto-Save
- Keyboard Shortcuts
- Dark Mode
- Error Handling
- Type Hints
- Logging
"""

import os
import logging
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QListWidget, QPushButton, QFileDialog,
    QToolBar, QMainWindow, QLabel, QSplitter, QMessageBox, 
    QInputDialog, QMenu, QMenuBar, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QTextCursor, QIcon, QKeySequence, QShortcut

from agent.openai_client import OpenAIClient
from agent.claude_client import ClaudeClient
from agent.drive_client import DriveClient
from utils.settings import Settings
from governance.canon_manager import CanonManager
from gui.writing_mode_dialog import WritingModeDialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WritingStudio(QMainWindow):
    """
    Full PyQt6 Writing Studio with enhanced features:
    - Sidebar for chapters
    - Rich text editor with word count
    - AI Generation / Revision (OpenAI or Claude)
    - Google Drive Save / Load (optional)
    - Local file save/load
    - Auto-save
    - Keyboard shortcuts
    - Dark mode support
    """

    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings = Settings()
        logger.info("Settings loaded")
        
        # Window Setup
        self.setWindowTitle("Novel Assistant Writing Studio")
        self.setGeometry(200, 200, 1400, 900)
        
        # Track current chapter
        self.current_filename: Optional[str] = None
        self.unsaved_changes = False
        
        # Core Services
        self._initialize_services()
        
        # UI Construction
        self._build_ui()
        self._setup_keyboard_shortcuts()
        self._setup_autosave()
        self._apply_theme()
        
        # Load sidebar
        self.refresh_chapter_list()
        
        # Connect editor text changes
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.textChanged.connect(self._update_word_count)

    # -----------------------------------------------------------
    # Service Initialization
    # -----------------------------------------------------------
    def _initialize_services(self) -> None:
        """Initialize AI and Drive clients based on settings."""
        # Initialize AI client based on provider setting
        provider = self.settings.get_ai_provider()
        self.ai = None
        
        try:
            if provider == "openai":
                self.ai = OpenAIClient()
                logger.info("OpenAI client initialized")
            elif provider == "claude":
                self.ai = ClaudeClient()
                logger.info("Claude client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            QMessageBox.warning(
                self, 
                "AI Client Error", 
                f"Could not initialize {provider.upper()} Client:\n{e}\n\nYou can change the provider in Settings."
            )
        
        # Initialize Drive client if enabled
        self.drive = None
        if self.settings.use_google_drive():
            try:
                self.drive = DriveClient()
                logger.info("Google Drive client initialized")
            except Exception as e:
                logger.warning(f"Google Drive initialization failed: {e}")
                QMessageBox.warning(
                    self, 
                    "Drive Error", 
                    f"Could not connect to Google Drive:\n{e}\n\nLocal file storage will be used instead."
                )
        
        # Initialize Canon Manager
        try:
            self.canon_manager = CanonManager(".")
            logger.info("Canon manager initialized")
        except Exception as e:
            logger.warning(f"Canon manager initialization failed: {e}")
            self.canon_manager = None

    # -----------------------------------------------------------
    # UI Setup
    # -----------------------------------------------------------
    def _build_ui(self) -> None:
        """Build the main UI components."""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        self.setCentralWidget(widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sidebar: Chapter List
        self.sidebar = QListWidget()
        self.sidebar.itemClicked.connect(self.load_selected_chapter)
        splitter.addWidget(self.sidebar)

        # Rich Text Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Start writing your chapter here...")
        
        # Apply editor settings
        font_family = self.settings.get("editor.font_family", "Consolas")
        font_size = self.settings.get("editor.font_size", 12)
        self.editor.setFontFamily(font_family)
        self.editor.setFontPointSize(font_size)
        
        if self.settings.get("editor.wrap_mode", True):
            self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        splitter.addWidget(self.editor)

        splitter.setSizes([300, 1100])
        main_layout.addWidget(splitter)

        # Menu Bar
        self._build_menu_bar()
        
        # Toolbar
        self._build_toolbar()

        # Status Bar
        self._build_status_bar()

    def _build_menu_bar(self) -> None:
        """Build the menu bar with all options."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Chapter", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.create_new_chapter)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Local File...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_local_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_current_chapter)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_as_chapter)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        if self.drive:
            save_drive_action = QAction("Save to &Drive", self)
            save_drive_action.triggered.connect(self.save_to_drive)
            file_menu.addAction(save_drive_action)
            
            load_drive_action = QAction("Load from &Drive", self)
            load_drive_action.triggered.connect(self.refresh_chapter_list)
            file_menu.addAction(load_drive_action)
            file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        generate_action = QAction("&Generate Text...", self)
        generate_action.setShortcut(QKeySequence("Ctrl+G"))
        generate_action.triggered.connect(self.generate_text)
        edit_menu.addAction(generate_action)
        
        revise_action = QAction("&Revise Selection...", self)
        revise_action.setShortcut(QKeySequence("Ctrl+R"))
        revise_action.triggered.connect(self.revise_selection)
        edit_menu.addAction(revise_action)
        
        edit_menu.addSeparator()
        
        # Writing Mode
        writing_mode_action = QAction("Enter &Writing Mode...", self)
        writing_mode_action.setShortcut(QKeySequence("Ctrl+W"))
        writing_mode_action.triggered.connect(self.enter_writing_mode)
        edit_menu.addAction(writing_mode_action)
        
        # Settings Menu
        settings_menu = menubar.addMenu("&Settings")
        
        ai_provider_menu = settings_menu.addMenu("&AI Provider")
        
        openai_action = QAction("&OpenAI", self)
        openai_action.setCheckable(True)
        openai_action.setChecked(self.settings.get_ai_provider() == "openai")
        openai_action.triggered.connect(lambda: self.set_ai_provider("openai"))
        ai_provider_menu.addAction(openai_action)
        
        claude_action = QAction("&Claude", self)
        claude_action.setCheckable(True)
        claude_action.setChecked(self.settings.get_ai_provider() == "claude")
        claude_action.triggered.connect(lambda: self.set_ai_provider("claude"))
        ai_provider_menu.addAction(claude_action)
        
        settings_menu.addSeparator()
        
        theme_menu = settings_menu.addMenu("&Theme")
        
        light_action = QAction("&Light", self)
        light_action.setCheckable(True)
        light_action.setChecked(self.settings.get_theme() == "light")
        light_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_action)
        
        dark_action = QAction("&Dark", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(self.settings.get_theme() == "dark")
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_action)
        
        settings_menu.addSeparator()
        
        autosave_action = QAction("&Auto-Save", self)
        autosave_action.setCheckable(True)
        autosave_action.setChecked(self.settings.is_autosave_enabled())
        autosave_action.triggered.connect(self.toggle_autosave)
        settings_menu.addAction(autosave_action)

    def _build_toolbar(self) -> None:
        """Build the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # New Chapter
        new_chapter_action = QAction("New Chapter", self)
        new_chapter_action.triggered.connect(self.create_new_chapter)
        toolbar.addAction(new_chapter_action)

        # Generate
        generate_action = QAction("Generate", self)
        generate_action.triggered.connect(self.generate_text)
        toolbar.addAction(generate_action)

        # Revise
        revise_action = QAction("Revise Selection", self)
        revise_action.triggered.connect(self.revise_selection)
        toolbar.addAction(revise_action)

        toolbar.addSeparator()

        # Save
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_current_chapter)
        toolbar.addAction(save_action)

        # Load
        load_action = QAction("Refresh List", self)
        load_action.triggered.connect(self.refresh_chapter_list)
        toolbar.addAction(load_action)
        
        toolbar.addSeparator()
        
        # Writing Mode
        writing_mode_toolbar_action = QAction("Writing Mode", self)
        writing_mode_toolbar_action.triggered.connect(self.enter_writing_mode)
        toolbar.addAction(writing_mode_toolbar_action)

    def _build_status_bar(self) -> None:
        """Build the status bar with word count."""
        self.status = QLabel("Ready.")
        self.statusBar().addWidget(self.status)
        
        # Word count label
        if self.settings.get("ui.word_count_enabled", True):
            self.word_count_label = QLabel("Words: 0")
            self.statusBar().addPermanentWidget(self.word_count_label)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Ctrl+S for save
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_chapter)
        
        # Ctrl+G for generate
        generate_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        generate_shortcut.activated.connect(self.generate_text)
        
        # Ctrl+R for revise
        revise_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        revise_shortcut.activated.connect(self.revise_selection)
        
        # Ctrl+N for new chapter
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.create_new_chapter)
        
        # Ctrl+O for open
        open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shortcut.activated.connect(self.open_local_file)
        
        # Ctrl+W for Writing Mode
        writing_mode_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        writing_mode_shortcut.activated.connect(self.enter_writing_mode)

    def _setup_autosave(self) -> None:
        """Setup auto-save timer."""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self._autosave)
        
        if self.settings.is_autosave_enabled():
            interval = self.settings.get_autosave_interval() * 1000  # Convert to milliseconds
            self.autosave_timer.start(interval)
            logger.info(f"Auto-save enabled with {interval/1000}s interval")

    def _apply_theme(self) -> None:
        """Apply light or dark theme."""
        theme = self.settings.get_theme()
        
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3c3c3c;
                }
                QListWidget {
                    background-color: #252526;
                    color: #cccccc;
                    border: 1px solid #3c3c3c;
                }
                QToolBar {
                    background-color: #2d2d30;
                    border: none;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #2d2d30;
                    color: #cccccc;
                }
                QMenu {
                    background-color: #2d2d30;
                    color: #cccccc;
                }
                QMenu::item:selected {
                    background-color: #094771;
                }
            """)
        else:
            self.setStyleSheet("")  # Default light theme

    # -----------------------------------------------------------
    # Event Handlers
    # -----------------------------------------------------------
    def _on_text_changed(self) -> None:
        """Handle text changes in editor."""
        self.unsaved_changes = True

    def _update_word_count(self) -> None:
        """Update word count display."""
        if hasattr(self, 'word_count_label'):
            text = self.editor.toPlainText()
            word_count = len(text.split()) if text.strip() else 0
            char_count = len(text)
            self.word_count_label.setText(f"Words: {word_count} | Characters: {char_count}")

    def _autosave(self) -> None:
        """Auto-save current chapter if there are unsaved changes."""
        if self.unsaved_changes and hasattr(self, 'current_filename') and self.current_filename:
            try:
                text = self.editor.toPlainText()
                self._save_local_file(self.current_filename, text)
                self.unsaved_changes = False
                logger.debug(f"Auto-saved: {self.current_filename}")
            except Exception as e:
                logger.error(f"Auto-save failed: {e}")

    def closeEvent(self, event) -> None:
        """Handle window close event with unsaved changes check."""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_chapter()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # -----------------------------------------------------------
    # CHAPTER MANAGEMENT
    # -----------------------------------------------------------
    def create_new_chapter(self) -> None:
        """Create a new chapter."""
        name, ok = QInputDialog.getText(self, "New Chapter", "Chapter name:")
        if ok and name:
            self.editor.clear()
            self.current_filename = f"{name}.txt"
            self.unsaved_changes = False
            self.status.setText(f"New chapter created: {self.current_filename}")
            logger.info(f"Created new chapter: {self.current_filename}")

    def refresh_chapter_list(self) -> None:
        """Reload sidebar with chapter names from Drive or local storage."""
        self.sidebar.clear()
        
        if self.drive is not None and self.settings.use_google_drive():
            try:
                chapters = self.drive.list_files(self.drive.chapters_folder)
                for c in chapters:
                    self.sidebar.addItem(c)
                self.status.setText("Chapter list refreshed from Drive.")
                logger.info("Refreshed chapter list from Google Drive")
            except Exception as e:
                logger.error(f"Failed to load from Drive: {e}")
                self._load_local_chapters()
        else:
            self._load_local_chapters()

    def _load_local_chapters(self) -> None:
        """Load chapter list from local storage."""
        chapters_path = Path(self.settings.get_local_chapters_path())
        chapters_path.mkdir(exist_ok=True)
        
        chapters = [f.name for f in chapters_path.glob("*.txt")]
        for c in sorted(chapters):
            self.sidebar.addItem(c)
        
        self.status.setText(f"Loaded {len(chapters)} local chapters.")
        logger.info(f"Loaded {len(chapters)} local chapters")

    def load_selected_chapter(self) -> None:
        """Load the clicked chapter into the editor."""
        if not self.sidebar.currentItem():
            return
            
        filename = self.sidebar.currentItem().text()
        text = None
        
        # Try Drive first if available
        if self.drive is not None and self.settings.use_google_drive():
            try:
                text = self.drive.load_text_file(self.drive.chapters_folder, filename)
            except Exception as e:
                logger.warning(f"Failed to load from Drive: {e}")
        
        # Fallback to local
        if text is None:
            text = self._load_local_file(filename)
        
        if text is not None:
            self.editor.setPlainText(text)
            self.current_filename = filename
            self.unsaved_changes = False
            self.status.setText(f"Loaded: {filename}")
            logger.info(f"Loaded chapter: {filename}")
        else:
            QMessageBox.warning(self, "Error", "Unable to load this chapter.")
            logger.error(f"Failed to load chapter: {filename}")

    def save_current_chapter(self) -> None:
        """Save text to local file or Drive."""
        if not hasattr(self, "current_filename") or not self.current_filename:
            self.save_as_chapter()
            return

        text = self.editor.toPlainText()
        
        # Save locally first
        self._save_local_file(self.current_filename, text)
        
        # Also save to Drive if available
        if self.drive is not None and self.settings.use_google_drive():
            try:
                self.drive.save_text_file(self.drive.chapters_folder, self.current_filename, text)
                self.status.setText(f"Saved to Drive and local: {self.current_filename}")
                logger.info(f"Saved to Drive and local: {self.current_filename}")
            except Exception as e:
                logger.warning(f"Failed to save to Drive: {e}")
                self.status.setText(f"Saved locally (Drive failed): {self.current_filename}")
        else:
            self.status.setText(f"Saved locally: {self.current_filename}")
            logger.info(f"Saved locally: {self.current_filename}")
        
        self.unsaved_changes = False

    def save_as_chapter(self) -> None:
        """Save chapter with a new name."""
        filename, ok = QFileDialog.getSaveFileName(
            self,
            "Save Chapter As",
            self.settings.get_local_chapters_path(),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if ok and filename:
            # Ensure .txt extension
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            self.current_filename = os.path.basename(filename)
            text = self.editor.toPlainText()
            self._save_local_file(self.current_filename, text)
            self.unsaved_changes = False
            self.refresh_chapter_list()
            logger.info(f"Saved as: {self.current_filename}")

    def open_local_file(self) -> None:
        """Open a local file."""
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Open Chapter",
            self.settings.get_local_chapters_path(),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if ok and filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.editor.setPlainText(text)
                self.current_filename = os.path.basename(filename)
                self.unsaved_changes = False
                self.status.setText(f"Opened: {self.current_filename}")
                logger.info(f"Opened file: {self.current_filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file:\n{e}")
                logger.error(f"Failed to open file: {e}")

    def save_to_drive(self) -> None:
        """Explicitly save to Google Drive."""
        if not self.drive:
            QMessageBox.warning(self, "Error", "Google Drive is not available.")
            return
        
        if not hasattr(self, "current_filename") or not self.current_filename:
            QMessageBox.warning(self, "Error", "No chapter is currently open.")
            return
        
        try:
            text = self.editor.toPlainText()
            self.drive.save_text_file(self.drive.chapters_folder, self.current_filename, text)
            self.status.setText(f"Saved to Drive: {self.current_filename}")
            logger.info(f"Saved to Drive: {self.current_filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save to Drive:\n{e}")
            logger.error(f"Failed to save to Drive: {e}")

    def _save_local_file(self, filename: str, text: str) -> None:
        """Save file to local storage."""
        chapters_path = Path(self.settings.get_local_chapters_path())
        chapters_path.mkdir(exist_ok=True)
        
        file_path = chapters_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def _load_local_file(self, filename: str) -> Optional[str]:
        """Load file from local storage."""
        chapters_path = Path(self.settings.get_local_chapters_path())
        file_path = chapters_path / filename
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to load local file: {e}")
                return None
        return None

    # -----------------------------------------------------------
    # AI GENERATION / REVISION
    # -----------------------------------------------------------
    def generate_text(self) -> None:
        """Generate text using AI."""
        prompt, ok = QInputDialog.getMultiLineText(
            self,
            "Generate with AI",
            "Describe what you want the AI to write:"
        )

        if not ok or not prompt.strip():
            return

        self.status.setText("Generating...")
        QApplication.processEvents()

        if self.ai:
            try:
                output = self.ai.generate_text(prompt)
                self.editor.append("\n" + output)
                self.status.setText("Generation complete.")
                logger.info("Text generation completed")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Generation failed:\n{e}")
                self.status.setText("Generation failed.")
                logger.error(f"Text generation failed: {e}")
        else:
            QMessageBox.warning(self, "Error", "AI Client not initialized.")
            self.status.setText("Generation failed.")

    def revise_selection(self) -> None:
        """Revise selected text using AI."""
        selected = self.editor.textCursor().selectedText()

        if not selected.strip():
            QMessageBox.warning(self, "Error", "No text selected for revision.")
            return

        instructions, ok = QInputDialog.getMultiLineText(
            self,
            "Revise Selection",
            "Describe how the selection should be revised:"
        )

        if not ok or not instructions.strip():
            return

        self.status.setText("Revising...")
        QApplication.processEvents()

        if self.ai:
            try:
                revised = self.ai.revise_text(selected, instructions)
                cursor = self.editor.textCursor()
                cursor.insertText(revised)
                self.status.setText("Revision complete.")
                logger.info("Text revision completed")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Revision failed:\n{e}")
                self.status.setText("Revision failed.")
                logger.error(f"Text revision failed: {e}")
        else:
            QMessageBox.warning(self, "Error", "AI Client not initialized.")
            self.status.setText("Revision failed.")

    # -----------------------------------------------------------
    # WRITING MODE
    # -----------------------------------------------------------
    def enter_writing_mode(self) -> None:
        """
        Open Writing Mode checklist dialog.
        
        This is a PRE-WRITING confirmation tool that prepares the system
        and author for focused writing. It protects focus and discipline.
        """
        # Get current chapter name
        current_chapter = None
        if hasattr(self, 'current_filename') and self.current_filename:
            # Remove .txt extension for display
            current_chapter = self.current_filename.replace('.txt', '')
        
        # Open Writing Mode dialog
        dialog = WritingModeDialog(
            self,
            canon_manager=self.canon_manager,
            current_chapter=current_chapter
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # User confirmed Writing Mode
            session_intent = dialog.get_session_intent()
            stop_on_momentum = dialog.should_stop_on_momentum_fade()
            
            # Update status
            if session_intent:
                self.status.setText(f"Writing Mode: {session_intent[:50]}...")
            else:
                self.status.setText("Writing Mode: Active")
            
            # Optional: Show brief confirmation
            if session_intent or stop_on_momentum:
                intent_msg = f"\nSession Intent: {session_intent}" if session_intent else ""
                momentum_msg = "\nWill stop when momentum fades." if stop_on_momentum else ""
                QMessageBox.information(
                    self,
                    "Writing Mode Active",
                    f"Writing Mode confirmed.{intent_msg}{momentum_msg}\n\nFocus on your writing."
                )
            
            logger.info("Writing Mode entered successfully")
        else:
            logger.info("Writing Mode cancelled")

    # -----------------------------------------------------------
    # SETTINGS MANAGEMENT
    # -----------------------------------------------------------
    def set_ai_provider(self, provider: str) -> None:
        """Switch AI provider and reinitialize client."""
        self.settings.set_ai_provider(provider)
        self._initialize_services()
        
        if self.ai:
            QMessageBox.information(
                self,
                "Provider Changed",
                f"AI provider switched to {provider.upper()}."
            )
            logger.info(f"AI provider switched to {provider}")
        else:
            QMessageBox.warning(
                self,
                "Provider Change Failed",
                f"Could not initialize {provider.upper()} client. Check your API key."
            )

    def set_theme(self, theme: str) -> None:
        """Switch theme."""
        self.settings.set_theme(theme)
        self._apply_theme()
        logger.info(f"Theme switched to {theme}")

    def toggle_autosave(self, enabled: bool) -> None:
        """Toggle auto-save on/off."""
        self.settings.set("autosave.enabled", enabled)
        if enabled:
            interval = self.settings.get_autosave_interval() * 1000
            self.autosave_timer.start(interval)
            logger.info("Auto-save enabled")
        else:
            self.autosave_timer.stop()
            logger.info("Auto-save disabled")


# -----------------------------------------------------------
# RUN APPLICATION
# -----------------------------------------------------------
def run_gui():
    """Run the GUI application."""
    app = QApplication([])
    window = WritingStudio()
    window.show()
    app.exec()


if __name__ == "__main__":
    run_gui()
