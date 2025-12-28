import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QListWidget, QPushButton, QFileDialog,
    QToolBar, QMainWindow, QLabel, QSplitter, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QTextCursor, QIcon

from agent.openai_client import OpenAIClient
from agent.drive_client import DriveClient


class WritingStudio(QMainWindow):
    """
    Full PyQt6 Writing Studio with:
    - Sidebar for chapters
    - Rich text editor
    - OpenAI Generation / Revision
    - Google Drive Save / Load
    """

    def __init__(self):
        super().__init__()

        # Window Setup
        self.setWindowTitle("Novel Assistant Writing Studio")
        self.setGeometry(200, 200, 1400, 900)

        # Core Services
        try:
            self.ai = OpenAIClient()
        except Exception as e:
            QMessageBox.warning(self, "AI Client Error", f"Could not initialize OpenAI Client:\n{e}")
            self.ai = None

        self.drive = DriveClient()

        # UI Construction
        self._build_ui()

        # Load sidebar
        self.refresh_chapter_list()

    # -----------------------------------------------------------
    # UI Setup
    # -----------------------------------------------------------
    def _build_ui(self):
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
        splitter.addWidget(self.editor)

        splitter.setSizes([300, 1100])
        main_layout.addWidget(splitter)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Buttons
        new_chapter_action = QAction("New Chapter", self)
        new_chapter_action.triggered.connect(self.create_new_chapter)
        toolbar.addAction(new_chapter_action)

        generate_action = QAction("Generate", self)
        generate_action.triggered.connect(self.generate_text)
        toolbar.addAction(generate_action)

        revise_action = QAction("Revise Selection", self)
        revise_action.triggered.connect(self.revise_selection)
        toolbar.addAction(revise_action)

        save_action = QAction("Save to Drive", self)
        save_action.triggered.connect(self.save_current_chapter)
        toolbar.addAction(save_action)

        load_action = QAction("Load from Drive", self)
        load_action.triggered.connect(self.refresh_chapter_list)
        toolbar.addAction(load_action)

        # Status Bar
        self.status = QLabel("Ready.")
        self.statusBar().addWidget(self.status)

    # -----------------------------------------------------------
    # CHAPTER MANAGEMENT
    # -----------------------------------------------------------
    def create_new_chapter(self):
        name, ok = QInputDialog.getText(self, "New Chapter", "Chapter name:")
        if ok and name:
            self.editor.clear()
            self.current_filename = f"{name}.txt"
            self.status.setText(f"New chapter created: {self.current_filename}")

    def refresh_chapter_list(self):
        """Reload sidebar with Google Drive chapter names."""

        self.sidebar.clear()
        chapters = self.drive.list_files(self.drive.chapters_folder)

        for c in chapters:
            self.sidebar.addItem(c)

        self.status.setText("Chapter list refreshed.")

    def load_selected_chapter(self):
        """Load the clicked chapter into the editor."""
        filename = self.sidebar.currentItem().text()
        text = self.drive.load_text_file(self.drive.chapters_folder, filename)

        if text is not None:
            self.editor.setPlainText(text)
            self.current_filename = filename
            self.status.setText(f"Loaded: {filename}")
        else:
            QMessageBox.warning(self, "Error", "Unable to load this chapter.")

    def save_current_chapter(self):
        """Save text to Google Drive."""
        if not hasattr(self, "current_filename"):
            QMessageBox.warning(self, "Error", "No chapter is currently open.")
            return

        text = self.editor.toPlainText()
        self.drive.save_text_file(self.drive.chapters_folder, self.current_filename, text)

        self.status.setText(f"Saved: {self.current_filename}")

    # -----------------------------------------------------------
    # AI GENERATION / REVISION
    # -----------------------------------------------------------
    def generate_text(self):
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
            output = self.ai.generate_text(prompt)
            self.editor.append("\n" + output)
            self.status.setText("Generation complete.")
        else:
            QMessageBox.warning(self, "Error", "AI Client not initialized.")
            self.status.setText("Generation failed.")

    def revise_selection(self):
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
            revised = self.ai.revise_text(selected, instructions)
            cursor = self.editor.textCursor()
            cursor.insertText(revised)
            self.status.setText("Revision complete.")
        else:
            QMessageBox.warning(self, "Error", "AI Client not initialized.")
            self.status.setText("Revision failed.")


# -----------------------------------------------------------
# RUN APPLICATION
# -----------------------------------------------------------
def run_gui():
    app = QApplication([])
    window = WritingStudio()
    window.show()
    app.exec()
