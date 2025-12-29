"""
Novel Assistant Writing Studio - Enhanced GUI
Features:
- Chapter upload and management
- Research document management
- AI prompt window for questions and revisions
- Model selection
- Review mode selection
- Batch processing
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QListWidget, QListWidgetItem, QTextEdit,
    QPushButton, QComboBox, QLabel, QFileDialog, QMessageBox,
    QProgressBar, QToolBar, QStatusBar, QInputDialog, QGroupBox,
    QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QMenu, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QFont, QColor, QIcon

# Import our modules (adjust path as needed)
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import get_router, get_model_choices_for_gui, ModelConfig
from services import (
    BatchReviewService, ReviewType, ReviewStatus,
    ReferenceLoader, extract_metadata_from_chapter
)


class ReviewWorker(QThread):
    """Background worker for batch reviews."""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, service: BatchReviewService, chapters: List[int], 
                 review_type: ReviewType, model_key: str):
        super().__init__()
        self.service = service
        self.chapters = chapters
        self.review_type = review_type
        self.model_key = model_key
    
    def run(self):
        try:
            self.service.set_progress_callback(
                lambda cur, tot, msg: self.progress.emit(cur, tot, msg)
            )
            result = self.service.run_batch_review(
                chapter_numbers=self.chapters if self.chapters else None,
                review_type=self.review_type,
                model_key=self.model_key
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class GenerateWorker(QThread):
    """Background worker for AI generation."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, model, prompt: str, config: Optional[ModelConfig] = None):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.config = config
    
    def run(self):
        try:
            response = self.model.generate(self.prompt, self.config)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class NovelAssistantStudio(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Novel Assistant Writing Studio")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Initialize services
        self.router = get_router()
        self.batch_service = BatchReviewService()
        self.reference_loader = ReferenceLoader()
        
        # State
        self.current_chapter_path: Optional[Path] = None
        self.worker: Optional[QThread] = None
        
        # Build UI
        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        
        # Load initial data
        self._refresh_chapter_list()
        self._refresh_research_list()
        self._update_model_status()
    
    def _build_ui(self):
        """Build the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL: File Management
        left_panel = self._build_left_panel()
        splitter.addWidget(left_panel)
        
        # CENTER PANEL: Editor
        center_panel = self._build_center_panel()
        splitter.addWidget(center_panel)
        
        # RIGHT PANEL: AI Assistant
        right_panel = self._build_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 700, 500])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def _build_left_panel(self) -> QWidget:
        """Build the left panel with chapters and research tabs."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        tabs = QTabWidget()
        
        # Chapters Tab
        chapters_widget = QWidget()
        chapters_layout = QVBoxLayout(chapters_widget)
        
        # Chapter list
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self._on_chapter_selected)
        self.chapter_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chapter_list.customContextMenuRequested.connect(self._chapter_context_menu)
        chapters_layout.addWidget(QLabel("Chapters"))
        chapters_layout.addWidget(self.chapter_list)
        
        # Chapter buttons
        btn_layout = QHBoxLayout()
        self.btn_upload_chapter = QPushButton("Upload")
        self.btn_upload_chapter.clicked.connect(self._upload_chapters)
        self.btn_new_chapter = QPushButton("New")
        self.btn_new_chapter.clicked.connect(self._new_chapter)
        self.btn_refresh_chapters = QPushButton("Refresh")
        self.btn_refresh_chapters.clicked.connect(self._refresh_chapter_list)
        btn_layout.addWidget(self.btn_upload_chapter)
        btn_layout.addWidget(self.btn_new_chapter)
        btn_layout.addWidget(self.btn_refresh_chapters)
        chapters_layout.addLayout(btn_layout)
        
        tabs.addTab(chapters_widget, "Chapters")
        
        # Research Tab
        research_widget = QWidget()
        research_layout = QVBoxLayout(research_widget)
        
        # Research tree
        self.research_tree = QTreeWidget()
        self.research_tree.setHeaderLabels(["Research Documents"])
        self.research_tree.itemDoubleClicked.connect(self._on_research_selected)
        research_layout.addWidget(self.research_tree)
        
        # Research buttons
        btn_layout2 = QHBoxLayout()
        self.btn_upload_research = QPushButton("Upload")
        self.btn_upload_research.clicked.connect(self._upload_research)
        self.btn_refresh_research = QPushButton("Refresh")
        self.btn_refresh_research.clicked.connect(self._refresh_research_list)
        btn_layout2.addWidget(self.btn_upload_research)
        btn_layout2.addWidget(self.btn_refresh_research)
        research_layout.addLayout(btn_layout2)
        
        tabs.addTab(research_widget, "Research")
        
        # Reference Tab
        reference_widget = QWidget()
        reference_layout = QVBoxLayout(reference_widget)
        
        self.reference_tree = QTreeWidget()
        self.reference_tree.setHeaderLabels(["Reference Files"])
        self.reference_tree.itemDoubleClicked.connect(self._on_reference_selected)
        reference_layout.addWidget(self.reference_tree)
        
        btn_layout3 = QHBoxLayout()
        self.btn_create_ref = QPushButton("Create")
        self.btn_create_ref.clicked.connect(self._create_reference)
        self.btn_refresh_ref = QPushButton("Refresh")
        self.btn_refresh_ref.clicked.connect(self._refresh_reference_list)
        btn_layout3.addWidget(self.btn_create_ref)
        btn_layout3.addWidget(self.btn_refresh_ref)
        reference_layout.addLayout(btn_layout3)
        
        tabs.addTab(reference_widget, "Reference")
        
        layout.addWidget(tabs)
        return panel
    
    def _build_center_panel(self) -> QWidget:
        """Build the center panel with the text editor."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Chapter info bar
        info_layout = QHBoxLayout()
        self.chapter_label = QLabel("No chapter loaded")
        self.chapter_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.chapter_label)
        info_layout.addStretch()
        
        self.word_count_label = QLabel("Words: 0")
        info_layout.addWidget(self.word_count_label)
        
        layout.addLayout(info_layout)
        
        # Main editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Load or create a chapter to begin editing...")
        self.editor.setFont(QFont("Georgia", 12))
        self.editor.textChanged.connect(self._update_word_count)
        layout.addWidget(self.editor)
        
        # Editor buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save Chapter")
        self.btn_save.clicked.connect(self._save_current_chapter)
        self.btn_save.setEnabled(False)
        
        self.btn_review_current = QPushButton("Review This Chapter")
        self.btn_review_current.clicked.connect(self._review_current_chapter)
        self.btn_review_current.setEnabled(False)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_review_current)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        return panel
    
    def _build_right_panel(self) -> QWidget:
        """Build the right panel with AI assistant."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Model Selection
        model_group = QGroupBox("AI Model")
        model_layout = QVBoxLayout(model_group)
        
        self.model_combo = QComboBox()
        self._populate_model_combo()
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)
        
        self.model_status = QLabel("Status: Checking...")
        model_layout.addWidget(self.model_status)
        
        layout.addWidget(model_group)
        
        # Review Controls
        review_group = QGroupBox("Batch Review")
        review_layout = QVBoxLayout(review_group)
        
        self.review_type_combo = QComboBox()
        self.review_type_combo.addItem("Full Review", ReviewType.FULL)
        self.review_type_combo.addItem("Consistency Check", ReviewType.CONSISTENCY)
        self.review_type_combo.addItem("Prose Quality", ReviewType.PROSE)
        self.review_type_combo.addItem("Historical Accuracy", ReviewType.HISTORICAL)
        review_layout.addWidget(QLabel("Review Type:"))
        review_layout.addWidget(self.review_type_combo)
        
        self.btn_batch_review = QPushButton("Run Batch Review (All Chapters)")
        self.btn_batch_review.clicked.connect(self._run_batch_review)
        review_layout.addWidget(self.btn_batch_review)
        
        self.btn_cancel_review = QPushButton("Cancel")
        self.btn_cancel_review.clicked.connect(self._cancel_review)
        self.btn_cancel_review.setEnabled(False)
        review_layout.addWidget(self.btn_cancel_review)
        
        layout.addWidget(review_group)
        
        # Prompt Window
        prompt_group = QGroupBox("AI Assistant")
        prompt_layout = QVBoxLayout(prompt_group)
        
        prompt_layout.addWidget(QLabel("Ask questions or request changes:"))
        
        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlaceholderText(
            "Examples:\n"
            "- Improve the dialogue in the selected text\n"
            "- Is this historically accurate for 1954?\n"
            "- Suggest a better opening for this scene\n"
            "- Check this passage for consistency with Rafael's character"
        )
        self.prompt_input.setMaximumHeight(150)
        prompt_layout.addWidget(self.prompt_input)
        
        prompt_btn_layout = QHBoxLayout()
        self.btn_send_prompt = QPushButton("Send")
        self.btn_send_prompt.clicked.connect(self._send_prompt)
        self.btn_revise_selection = QPushButton("Revise Selection")
        self.btn_revise_selection.clicked.connect(self._revise_selection)
        prompt_btn_layout.addWidget(self.btn_send_prompt)
        prompt_btn_layout.addWidget(self.btn_revise_selection)
        prompt_layout.addLayout(prompt_btn_layout)
        
        # Response area
        prompt_layout.addWidget(QLabel("AI Response:"))
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.response_area.setPlaceholderText("AI responses will appear here...")
        prompt_layout.addWidget(self.response_area)
        
        # Response actions
        response_btn_layout = QHBoxLayout()
        self.btn_apply_response = QPushButton("Apply to Editor")
        self.btn_apply_response.clicked.connect(self._apply_response)
        self.btn_copy_response = QPushButton("Copy")
        self.btn_copy_response.clicked.connect(self._copy_response)
        response_btn_layout.addWidget(self.btn_apply_response)
        response_btn_layout.addWidget(self.btn_copy_response)
        prompt_layout.addLayout(response_btn_layout)
        
        layout.addWidget(prompt_group)
        
        return panel
    
    def _build_menu(self):
        """Build the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        upload_action = QAction("Upload Chapters...", self)
        upload_action.triggered.connect(self._upload_chapters)
        file_menu.addAction(upload_action)
        
        upload_research_action = QAction("Upload Research...", self)
        upload_research_action.triggered.connect(self._upload_research)
        file_menu.addAction(upload_research_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save Chapter", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_current_chapter)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Review menu
        review_menu = menubar.addMenu("Review")
        
        review_current_action = QAction("Review Current Chapter", self)
        review_current_action.triggered.connect(self._review_current_chapter)
        review_menu.addAction(review_current_action)
        
        batch_action = QAction("Batch Review All Chapters", self)
        batch_action.triggered.connect(self._run_batch_review)
        review_menu.addAction(batch_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _build_toolbar(self):
        """Build the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        toolbar.addAction("Upload Chapters", self._upload_chapters)
        toolbar.addAction("Upload Research", self._upload_research)
        toolbar.addSeparator()
        toolbar.addAction("Save", self._save_current_chapter)
        toolbar.addSeparator()
        toolbar.addAction("Review Chapter", self._review_current_chapter)
        toolbar.addAction("Batch Review", self._run_batch_review)
    
    def _populate_model_combo(self):
        """Populate the model selection combo box."""
        self.model_combo.clear()
        for display, key in get_model_choices_for_gui():
            self.model_combo.addItem(display, key)
        
        # Set default to Claude Sonnet
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == "claude-sonnet":
                self.model_combo.setCurrentIndex(i)
                break
    
    def _update_model_status(self):
        """Update the model availability status."""
        model_key = self.model_combo.currentData()
        if model_key:
            model = self.router.get_model(model_key)
            if model and model.is_available():
                self.model_status.setText(f"✓ Ready | Context: {model.max_context:,} tokens")
                self.model_status.setStyleSheet("color: green;")
            else:
                self.model_status.setText("✗ API key not configured")
                self.model_status.setStyleSheet("color: red;")
    
    def _on_model_changed(self):
        """Handle model selection change."""
        model_key = self.model_combo.currentData()
        if model_key:
            self.router.set_current_model(model_key)
            self._update_model_status()
    
    def _refresh_chapter_list(self):
        """Refresh the chapter list."""
        self.chapter_list.clear()
        chapters = self.batch_service.list_chapters()
        
        for ch in chapters:
            item = QListWidgetItem(f"Ch {ch['number']}: {ch['title']}" if ch['title'] else ch['filename'])
            item.setData(Qt.ItemDataRole.UserRole, ch)
            self.chapter_list.addItem(item)
        
        self.status_bar.showMessage(f"Loaded {len(chapters)} chapters", 3000)
    
    def _refresh_research_list(self):
        """Refresh the research document tree."""
        self.research_tree.clear()
        research = self.batch_service.list_research()
        
        # Group by category
        categories = {}
        for r in research:
            cat = r['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, files in sorted(categories.items()):
            cat_item = QTreeWidgetItem([cat])
            for f in files:
                file_item = QTreeWidgetItem([f['filename']])
                file_item.setData(0, Qt.ItemDataRole.UserRole, f)
                cat_item.addChild(file_item)
            self.research_tree.addTopLevelItem(cat_item)
        
        self.research_tree.expandAll()
    
    def _refresh_reference_list(self):
        """Refresh the reference files tree."""
        self.reference_tree.clear()
        
        categories = {
            "Characters": self.reference_loader.get_available_characters(),
            "Locations": self.reference_loader.get_available_locations(),
            "Historical": self.reference_loader.get_available_historical_topics()
        }
        
        for cat, items in categories.items():
            cat_item = QTreeWidgetItem([cat])
            for item in items:
                file_item = QTreeWidgetItem([item])
                cat_item.addChild(file_item)
            self.reference_tree.addTopLevelItem(cat_item)
        
        self.reference_tree.expandAll()
    
    def _upload_chapters(self):
        """Upload chapter files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Chapter Files",
            "",
            "Text Files (*.txt *.md);;Word Documents (*.docx);;All Files (*.*)"
        )
        
        if files:
            for f in files:
                src = Path(f)
                dst = self.batch_service.chapters_dir / src.name
                shutil.copy2(src, dst)
            
            self._refresh_chapter_list()
            self.status_bar.showMessage(f"Uploaded {len(files)} chapter(s)", 3000)
    
    def _upload_research(self):
        """Upload research documents."""
        # Ask for category
        categories = ["general", "characters", "locations", "timeline", "historical", "custom"]
        category, ok = QInputDialog.getItem(
            self, "Select Category", "Research Category:", categories, 0, False
        )
        
        if not ok:
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Research Files",
            "",
            "Documents (*.txt *.md *.docx *.pdf);;All Files (*.*)"
        )
        
        if files:
            target_dir = self.batch_service.research_dir / category
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for f in files:
                src = Path(f)
                dst = target_dir / src.name
                shutil.copy2(src, dst)
            
            self._refresh_research_list()
            self.status_bar.showMessage(f"Uploaded {len(files)} research file(s)", 3000)
    
    def _new_chapter(self):
        """Create a new chapter."""
        number, ok = QInputDialog.getInt(
            self, "New Chapter", "Chapter Number:", 1, 1, 100
        )
        if not ok:
            return
        
        title, ok = QInputDialog.getText(
            self, "New Chapter", "Chapter Title (optional):"
        )
        
        filename = f"chapter_{number:02d}"
        if title:
            filename += f"_{title.lower().replace(' ', '_')}"
        filename += ".md"
        
        # Create with template
        content = f"""---
chapter: {number}
title: {title}
characters: []
locations: []
dates: []
historical: []
---

# Chapter {number}{': ' + title if title else ''}

"""
        
        self.batch_service.save_chapter(filename, content)
        self._refresh_chapter_list()
        
        # Load the new chapter
        self.current_chapter_path = self.batch_service.chapters_dir / filename
        self.editor.setPlainText(content)
        self.chapter_label.setText(f"Chapter {number}: {title}" if title else f"Chapter {number}")
        self.btn_save.setEnabled(True)
        self.btn_review_current.setEnabled(True)
    
    def _on_chapter_selected(self, item: QListWidgetItem):
        """Handle chapter selection."""
        chapter_info = item.data(Qt.ItemDataRole.UserRole)
        if not chapter_info:
            return
        
        content = self.batch_service.load_chapter(chapter_info['filename'])
        if content:
            self.editor.setPlainText(content)
            self.current_chapter_path = Path(chapter_info['path'])
            title = chapter_info['title'] or chapter_info['filename']
            self.chapter_label.setText(f"Chapter {chapter_info['number']}: {title}")
            self.btn_save.setEnabled(True)
            self.btn_review_current.setEnabled(True)
            self._update_word_count()
        else:
            QMessageBox.warning(self, "Error", f"Could not load chapter: {chapter_info['filename']}")
    
    def _on_research_selected(self, item: QTreeWidgetItem, column: int):
        """Handle research document selection."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        # Load and display in response area
        path = Path(data['path'])
        try:
            content = path.read_text(encoding="utf-8")
            self.response_area.setPlainText(f"=== {data['filename']} ===\n\n{content}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load file: {e}")
    
    def _on_reference_selected(self, item: QTreeWidgetItem, column: int):
        """Handle reference file selection."""
        if item.childCount() > 0:  # It's a category
            return
        
        name = item.text(0)
        parent = item.parent()
        if not parent:
            return
        
        category = parent.text(0).lower()
        
        if category == "characters":
            content = self.reference_loader.load_character_ref(name)
        elif category == "locations":
            content = self.reference_loader.load_location_ref(name)
        elif category == "historical":
            content = self.reference_loader.load_historical_ref(name)
        else:
            return
        
        if content:
            self.response_area.setPlainText(f"=== {name} ({category}) ===\n\n{content}")
    
    def _create_reference(self):
        """Create a new reference file."""
        categories = ["characters", "locations", "historical", "custom"]
        category, ok = QInputDialog.getItem(
            self, "Create Reference", "Category:", categories, 0, False
        )
        if not ok:
            return
        
        name, ok = QInputDialog.getText(
            self, "Create Reference", "Reference Name:"
        )
        if not ok or not name:
            return
        
        content, ok = QInputDialog.getMultiLineText(
            self, "Create Reference", "Reference Content:"
        )
        if not ok:
            return
        
        if self.reference_loader.save_reference(category, name, content):
            self._refresh_reference_list()
            self.status_bar.showMessage(f"Created reference: {name}", 3000)
        else:
            QMessageBox.warning(self, "Error", "Could not save reference file")
    
    def _chapter_context_menu(self, position):
        """Show context menu for chapter list."""
        item = self.chapter_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        review_action = menu.addAction("Review This Chapter")
        delete_action = menu.addAction("Delete Chapter")
        
        action = menu.exec(self.chapter_list.mapToGlobal(position))
        
        if action == review_action:
            self._on_chapter_selected(item)
            self._review_current_chapter()
        elif action == delete_action:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete {item.text()}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                data = item.data(Qt.ItemDataRole.UserRole)
                Path(data['path']).unlink()
                self._refresh_chapter_list()
    
    def _save_current_chapter(self):
        """Save the current chapter."""
        if not self.current_chapter_path:
            return
        
        content = self.editor.toPlainText()
        try:
            self.current_chapter_path.write_text(content, encoding="utf-8")
            self.status_bar.showMessage("Chapter saved", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save: {e}")
    
    def _update_word_count(self):
        """Update the word count display."""
        text = self.editor.toPlainText()
        words = len(text.split())
        self.word_count_label.setText(f"Words: {words:,}")
    
    def _review_current_chapter(self):
        """Review the currently loaded chapter."""
        if not self.current_chapter_path:
            QMessageBox.warning(self, "Error", "No chapter loaded")
            return
        
        model_key = self.model_combo.currentData()
        model = self.router.get_model(model_key)
        
        if not model or not model.is_available():
            QMessageBox.warning(self, "Error", "Selected AI model is not available")
            return
        
        content = self.editor.toPlainText()
        review_type = self.review_type_combo.currentData()
        
        # Get reference context
        metadata = extract_metadata_from_chapter(content, 0)
        bundle = self.reference_loader.load_bundle_for_chapter(metadata)
        if not bundle.master_reference:
            bundle = self.reference_loader.load_full_bundle()
        
        reference_context = bundle.get_combined_context(max_tokens=30000)
        
        self.status_bar.showMessage("Reviewing chapter...")
        self.response_area.setPlainText("Reviewing chapter, please wait...")
        
        # Run in background
        config = ModelConfig(max_tokens=4000)
        
        def on_finished(response):
            if response.success:
                self.response_area.setPlainText(response.text)
                self.status_bar.showMessage(
                    f"Review complete | Tokens: {response.tokens_used:,} | Cost: ${response.cost_estimate:.4f}",
                    5000
                )
            else:
                self.response_area.setPlainText(f"Error: {response.error_message}")
                self.status_bar.showMessage("Review failed", 3000)
        
        # Simple blocking call for now (could be threaded)
        response = model.review_chapter(content, reference_context, review_type.value, config)
        on_finished(response)
    
    def _run_batch_review(self):
        """Run batch review on all chapters."""
        chapters = self.batch_service.list_chapters()
        if not chapters:
            QMessageBox.warning(self, "Error", "No chapters found to review")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Batch Review",
            f"Review all {len(chapters)} chapters?\n\nThis may take several minutes and use API tokens.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        model_key = self.model_combo.currentData()
        review_type = self.review_type_combo.currentData()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(chapters))
        self.progress_bar.setValue(0)
        self.btn_batch_review.setEnabled(False)
        self.btn_cancel_review.setEnabled(True)
        
        self.worker = ReviewWorker(
            self.batch_service,
            chapters=None,  # All chapters
            review_type=review_type,
            model_key=model_key
        )
        
        self.worker.progress.connect(self._on_review_progress)
        self.worker.finished.connect(self._on_batch_finished)
        self.worker.error.connect(self._on_batch_error)
        self.worker.start()
    
    def _cancel_review(self):
        """Cancel the ongoing batch review."""
        if self.worker:
            self.batch_service.cancel()
            self.status_bar.showMessage("Cancelling...")
    
    def _on_review_progress(self, current: int, total: int, message: str):
        """Handle review progress updates."""
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(message)
    
    def _on_batch_finished(self, result):
        """Handle batch review completion."""
        self.progress_bar.setVisible(False)
        self.btn_batch_review.setEnabled(True)
        self.btn_cancel_review.setEnabled(False)
        
        self.response_area.setPlainText(result.summary)
        
        QMessageBox.information(
            self, "Batch Review Complete",
            f"Reviewed {result.completed}/{result.total_chapters} chapters\n"
            f"Total tokens: {result.total_tokens:,}\n"
            f"Estimated cost: ${result.total_cost:.4f}\n\n"
            f"Results saved to reviews/ directory"
        )
    
    def _on_batch_error(self, error: str):
        """Handle batch review error."""
        self.progress_bar.setVisible(False)
        self.btn_batch_review.setEnabled(True)
        self.btn_cancel_review.setEnabled(False)
        
        QMessageBox.critical(self, "Error", f"Batch review failed: {error}")
    
    def _send_prompt(self):
        """Send a prompt to the AI."""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            return
        
        model_key = self.model_combo.currentData()
        model = self.router.get_model(model_key)
        
        if not model or not model.is_available():
            QMessageBox.warning(self, "Error", "Selected AI model is not available")
            return
        
        # Include chapter context if loaded
        chapter_context = ""
        if self.current_chapter_path:
            chapter_text = self.editor.toPlainText()
            chapter_context = f"\n\n## CURRENT CHAPTER CONTEXT\n{chapter_text[:5000]}..."
        
        full_prompt = prompt_text + chapter_context
        
        self.response_area.setPlainText("Generating response...")
        self.status_bar.showMessage("Sending prompt to AI...")
        
        response = model.generate(full_prompt, ModelConfig(max_tokens=2000))
        
        if response.success:
            self.response_area.setPlainText(response.text)
            self.status_bar.showMessage(
                f"Response received | Tokens: {response.tokens_used:,}",
                3000
            )
        else:
            self.response_area.setPlainText(f"Error: {response.error_message}")
    
    def _revise_selection(self):
        """Revise the selected text in the editor."""
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        
        if not selected:
            QMessageBox.warning(self, "Error", "Please select text to revise")
            return
        
        instructions = self.prompt_input.toPlainText().strip()
        if not instructions:
            QMessageBox.warning(self, "Error", "Please enter revision instructions")
            return
        
        model_key = self.model_combo.currentData()
        model = self.router.get_model(model_key)
        
        if not model or not model.is_available():
            QMessageBox.warning(self, "Error", "Selected AI model is not available")
            return
        
        self.response_area.setPlainText("Revising selection...")
        
        response = model.revise_text(selected, instructions)
        
        if response.success:
            self.response_area.setPlainText(response.text)
            self.status_bar.showMessage("Revision ready - click 'Apply to Editor' to use", 5000)
        else:
            self.response_area.setPlainText(f"Error: {response.error_message}")
    
    def _apply_response(self):
        """Apply the AI response to the editor."""
        response_text = self.response_area.toPlainText()
        if not response_text:
            return
        
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # Replace selection
            cursor.insertText(response_text)
        else:
            # Append at cursor
            cursor.insertText("\n\n" + response_text)
        
        self.status_bar.showMessage("Applied to editor", 3000)
    
    def _copy_response(self):
        """Copy response to clipboard."""
        response_text = self.response_area.toPlainText()
        if response_text:
            QApplication.clipboard().setText(response_text)
            self.status_bar.showMessage("Copied to clipboard", 2000)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Novel Assistant",
            "Novel Assistant Writing Studio\n\n"
            "A professional tool for novel writing and AI-assisted review.\n\n"
            "Features:\n"
            "• Chapter management and editing\n"
            "• Research document organization\n"
            "• AI-powered chapter review\n"
            "• Multi-model support (Claude, GPT, Gemini)\n"
            "• Token-efficient reference loading"
        )


def run_gui():
    """Run the GUI application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = NovelAssistantStudio()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
