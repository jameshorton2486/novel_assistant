"""
Novel Assistant v3 - Integrated Tabbed Interface
Connects all backend services to PyQt6 GUI.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QListWidget, QPushButton, QFileDialog, QLabel,
    QComboBox, QTabWidget, QSplitter, QMessageBox, QProgressBar,
    QStatusBar, QMenuBar, QMenu, QToolBar, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QTreeWidget, QTreeWidgetItem, QGroupBox,
    QCheckBox, QInputDialog, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QKeySequence

from models.model_router import ModelRouter, ModelType
from governance.canon_manager import CanonManager, ChapterState
from governance.regression_checker import RegressionChecker
from services.research_digestor import ResearchDigestor, ResearchClass, ResearchStatus
from services.era_linter import EraLinter
from services.advisor_mode import AdvisorMode
from export.docx_exporter import DocxExporter
from export.epub_exporter import EpubExporter
from export.query_builder import QueryBuilder
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


class NovelAssistantApp(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Novel Assistant v3")
        self.setGeometry(100, 100, 1400, 900)
        
        # Base path
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Current chapter tracking
        self.current_chapter: Optional[str] = None
        
        # Initialize backend services
        self._init_services()
        
        # Build UI
        self._init_ui()
        self._init_menu()
        self._init_statusbar()
        
        logger.info("Novel Assistant v3 initialized")
    
    def _init_services(self) -> None:
        """Initialize all backend services."""
        try:
            self.model_router = ModelRouter()
            logger.info("Model router initialized")
        except Exception as e:
            logger.error(f"Model router init failed: {e}")
            self.model_router = None
        
        try:
            self.canon_manager = CanonManager(self.base_path)
            logger.info("Canon manager initialized")
        except Exception as e:
            logger.warning(f"Canon manager init failed: {e}")
            self.canon_manager = None
        
        try:
            if self.canon_manager:
                self.regression_checker = RegressionChecker(self.canon_manager, self.base_path)
                logger.info("Regression checker initialized")
            else:
                self.regression_checker = None
        except Exception as e:
            logger.warning(f"Regression checker init failed: {e}")
            self.regression_checker = None
        
        try:
            if self.model_router:
                self.research_digestor = ResearchDigestor(self.base_path, self.model_router)
                logger.info("Research digestor initialized")
            else:
                self.research_digestor = None
        except Exception as e:
            logger.warning(f"Research digestor init failed: {e}")
            self.research_digestor = None
        
        try:
            self.era_linter = EraLinter()
            logger.info("Era linter initialized")
        except Exception as e:
            logger.warning(f"Era linter init failed: {e}")
            self.era_linter = None
        
        try:
            if self.model_router and self.canon_manager and self.era_linter:
                self.advisor_mode = AdvisorMode(self.model_router, self.canon_manager, self.era_linter)
                logger.info("Advisor mode initialized")
            else:
                self.advisor_mode = None
        except Exception as e:
            logger.warning(f"Advisor mode init failed: {e}")
            self.advisor_mode = None
        
        # Export services (optional dependencies)
        try:
            self.docx_exporter = DocxExporter()
            logger.info("DOCX exporter initialized")
        except Exception as e:
            logger.warning(f"DOCX exporter not available: {e}")
            self.docx_exporter = None
        
        try:
            self.epub_exporter = EpubExporter()
            logger.info("EPUB exporter initialized")
        except Exception as e:
            logger.warning(f"EPUB exporter not available: {e}")
            self.epub_exporter = None
        
        try:
            if self.model_router:
                self.query_builder = QueryBuilder(self.base_path)
                logger.info("Query builder initialized")
            else:
                self.query_builder = None
        except Exception as e:
            logger.warning(f"Query builder init failed: {e}")
            self.query_builder = None
    
    def _init_ui(self) -> None:
        """Build the main UI with tabs."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.tabs.addTab(self._create_editor_tab(), "📝 Editor")
        self.tabs.addTab(self._create_research_tab(), "📚 Research")
        self.tabs.addTab(self._create_canon_tab(), "📖 Canon")
        self.tabs.addTab(self._create_advisor_tab(), "🎯 Advisor")
        self.tabs.addTab(self._create_export_tab(), "📤 Export")
    
    def _create_editor_tab(self) -> QWidget:
        """Main writing/editing interface."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Left panel - Chapter list
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Chapters"))
        
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self._load_chapter)
        left_panel.addWidget(self.chapter_list)
        
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("New")
        btn_new.clicked.connect(self._new_chapter)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_chapter)
        btn_layout.addWidget(btn_new)
        btn_layout.addWidget(btn_save)
        left_panel.addLayout(btn_layout)
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(200)
        
        # Center panel - Editor
        center_panel = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Claude Sonnet", "Claude Haiku", "GPT-4o", "Gemini Pro"])
        toolbar.addWidget(self.model_combo)
        
        btn_lint = QPushButton("🔍 Era Lint")
        btn_lint.clicked.connect(self._run_era_lint)
        toolbar.addWidget(btn_lint)
        
        btn_advisor = QPushButton("💡 Quick Advice")
        btn_advisor.clicked.connect(self._run_quick_advice)
        toolbar.addWidget(btn_advisor)
        
        btn_writing_mode = QPushButton("✍️ Writing Mode")
        btn_writing_mode.clicked.connect(self._enter_writing_mode)
        toolbar.addWidget(btn_writing_mode)
        
        toolbar.addStretch()
        center_panel.addLayout(toolbar)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 12))
        self.editor.setPlaceholderText("Start writing or load a chapter...")
        center_panel.addWidget(self.editor)
        
        # Word count
        self.word_count_label = QLabel("Words: 0")
        self.editor.textChanged.connect(self._update_word_count)
        center_panel.addWidget(self.word_count_label)
        
        center_widget = QWidget()
        center_widget.setLayout(center_panel)
        
        # Right panel - AI Assistant
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("AI Assistant"))
        
        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setMaximumWidth(350)
        right_panel.addWidget(self.ai_output)
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask AI for help...")
        self.ai_input.returnPressed.connect(self._send_to_ai)
        right_panel.addWidget(self.ai_input)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setMaximumWidth(350)
        
        # Add to main layout
        layout.addWidget(left_widget)
        layout.addWidget(center_widget, stretch=1)
        layout.addWidget(right_widget)
        
        # Load chapters
        self._refresh_chapter_list()
        
        return widget
    
    def _create_research_tab(self) -> QWidget:
        """Research document management."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Left - Document list
        left = QVBoxLayout()
        left.addWidget(QLabel("Research Documents"))
        
        self.research_list = QTreeWidget()
        self.research_list.setHeaderLabels(["Document", "Status", "Class"])
        self.research_list.itemClicked.connect(self._on_research_item_clicked)
        self._refresh_research_list()
        left.addWidget(self.research_list)
        
        btn_ingest = QPushButton("📥 Ingest New Document")
        btn_ingest.clicked.connect(self._ingest_research)
        left.addWidget(btn_ingest)
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        
        # Right - Document details & actions
        right = QVBoxLayout()
        right.addWidget(QLabel("Document Processing"))
        
        # Intent selection
        intent_group = QGroupBox("Classification")
        intent_layout = QFormLayout()
        
        self.intent_input = QLineEdit()
        self.intent_input.setPlaceholderText("e.g., Historical Context, Location Reference")
        intent_layout.addRow("Intent:", self.intent_input)
        
        self.class_combo = QComboBox()
        self.class_combo.addItems(["canon", "context", "artifact", "craft"])
        intent_layout.addRow("Class:", self.class_combo)
        
        intent_group.setLayout(intent_layout)
        right.addWidget(intent_group)
        
        # Action buttons
        btn_classify = QPushButton("📋 Classify")
        btn_classify.clicked.connect(self._classify_research)
        right.addWidget(btn_classify)
        
        btn_distill = QPushButton("🧪 Distill (AI)")
        btn_distill.clicked.connect(self._distill_research)
        right.addWidget(btn_distill)
        
        btn_promote = QPushButton("⬆️ Promote")
        btn_promote.clicked.connect(self._promote_research)
        right.addWidget(btn_promote)
        
        btn_reject = QPushButton("❌ Reject")
        btn_reject.clicked.connect(self._reject_research)
        right.addWidget(btn_reject)
        
        right.addStretch()
        
        # Stats
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        self.research_stats = QLabel("Loading...")
        stats_layout.addWidget(self.research_stats)
        stats_group.setLayout(stats_layout)
        right.addWidget(stats_group)
        
        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setMaximumWidth(300)
        
        layout.addWidget(left_widget, stretch=1)
        layout.addWidget(right_widget)
        
        self._update_research_stats()
        
        return widget
    
    def _create_canon_tab(self) -> QWidget:
        """Canon management and consistency checking."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Left - Canon facts
        left = QVBoxLayout()
        left.addWidget(QLabel("Canon Facts"))
        
        self.canon_tree = QTreeWidget()
        self.canon_tree.setHeaderLabels(["Fact", "Value", "Source"])
        self._refresh_canon_tree()
        left.addWidget(self.canon_tree)
        
        btn_add_fact = QPushButton("➕ Add Fact")
        btn_add_fact.clicked.connect(self._add_canon_fact)
        left.addWidget(btn_add_fact)
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        
        # Center - Chapter states
        center = QVBoxLayout()
        center.addWidget(QLabel("Chapter Lock States"))
        
        self.chapter_state_list = QTreeWidget()
        self.chapter_state_list.setHeaderLabels(["Chapter", "State"])
        self._refresh_chapter_states()
        center.addWidget(self.chapter_state_list)
        
        state_btns = QHBoxLayout()
        btn_lock = QPushButton("🔒 Lock")
        btn_lock.clicked.connect(lambda: self._set_chapter_state(ChapterState.CANON_LOCKED))
        btn_unlock = QPushButton("🔓 Unlock")
        btn_unlock.clicked.connect(lambda: self._set_chapter_state(ChapterState.DRAFT))
        state_btns.addWidget(btn_lock)
        state_btns.addWidget(btn_unlock)
        center.addLayout(state_btns)
        
        center_widget = QWidget()
        center_widget.setLayout(center)
        
        # Right - Regression checks
        right = QVBoxLayout()
        right.addWidget(QLabel("Consistency Checks"))
        
        btn_run_checks = QPushButton("🔍 Run All Checks")
        btn_run_checks.clicked.connect(self._run_regression_checks)
        right.addWidget(btn_run_checks)
        
        self.regression_output = QTextEdit()
        self.regression_output.setReadOnly(True)
        right.addWidget(self.regression_output)
        
        right_widget = QWidget()
        right_widget.setLayout(right)
        
        layout.addWidget(left_widget)
        layout.addWidget(center_widget)
        layout.addWidget(right_widget)
        
        return widget
    
    def _create_advisor_tab(self) -> QWidget:
        """AI editorial advisor."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Select Chapter:"))
        
        self.advisor_chapter_combo = QComboBox()
        self._refresh_advisor_chapters()
        controls.addWidget(self.advisor_chapter_combo)
        
        btn_analyze = QPushButton("🎯 Analyze Chapter")
        btn_analyze.clicked.connect(self._run_advisor_analysis)
        controls.addWidget(btn_analyze)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Results
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left - Era lint results
        era_widget = QWidget()
        era_layout = QVBoxLayout(era_widget)
        era_layout.addWidget(QLabel("Era Language Issues"))
        self.era_lint_output = QTextEdit()
        self.era_lint_output.setReadOnly(True)
        era_layout.addWidget(self.era_lint_output)
        splitter.addWidget(era_widget)
        
        # Center - Recommendations
        rec_widget = QWidget()
        rec_layout = QVBoxLayout(rec_widget)
        rec_layout.addWidget(QLabel("Recommendations"))
        self.rec_output = QTextEdit()
        self.rec_output.setReadOnly(True)
        rec_layout.addWidget(self.rec_output)
        splitter.addWidget(rec_widget)
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_export_tab(self) -> QWidget:
        """Export and publishing tools."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Metadata section
        meta_group = QGroupBox("Manuscript Metadata")
        meta_layout = QFormLayout()
        
        self.export_title = QLineEdit()
        self.export_title.setPlaceholderText("Novel Title")
        meta_layout.addRow("Title:", self.export_title)
        
        self.export_author = QLineEdit()
        self.export_author.setPlaceholderText("Author Name")
        meta_layout.addRow("Author:", self.export_author)
        
        meta_group.setLayout(meta_layout)
        layout.addWidget(meta_group)
        
        # Export buttons
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()
        
        btn_docx = QPushButton("📄 Export DOCX (Standard Manuscript)")
        btn_docx.clicked.connect(self._export_docx)
        btn_docx.setEnabled(self.docx_exporter is not None)
        export_layout.addWidget(btn_docx)
        
        btn_epub = QPushButton("📱 Export EPUB (E-Reader)")
        btn_epub.clicked.connect(self._export_epub)
        btn_epub.setEnabled(self.epub_exporter is not None)
        export_layout.addWidget(btn_epub)
        
        btn_query = QPushButton("📬 Build Query Package")
        btn_query.clicked.connect(self._build_query_package)
        btn_query.setEnabled(self.query_builder is not None)
        export_layout.addWidget(btn_query)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Status
        self.export_status = QTextEdit()
        self.export_status.setReadOnly(True)
        self.export_status.setMaximumHeight(200)
        layout.addWidget(self.export_status)
        
        layout.addStretch()
        
        return widget
    
    # -----------------------------------------------------------
    # EDITOR TAB METHODS
    # -----------------------------------------------------------
    
    def _update_word_count(self) -> None:
        """Update word count display."""
        text = self.editor.toPlainText()
        count = len(text.split()) if text.strip() else 0
        self.word_count_label.setText(f"Words: {count:,}")
    
    def _refresh_chapter_list(self) -> None:
        """Refresh chapter list from filesystem."""
        self.chapter_list.clear()
        chapters_dir = os.path.join(self.base_path, "chapters")
        if os.path.exists(chapters_dir):
            for f in sorted(os.listdir(chapters_dir)):
                if f.endswith(('.md', '.txt')):
                    self.chapter_list.addItem(f)
    
    def _load_chapter(self, item: QListWidgetItem) -> None:
        """Load chapter into editor."""
        filename = item.text()
        filepath = os.path.join(self.base_path, "chapters", filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_chapter = filename
                self.statusBar().showMessage(f"Loaded: {filename}")
                logger.info(f"Loaded chapter: {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load chapter:\n{e}")
                logger.error(f"Error loading chapter: {e}")
    
    def _save_chapter(self) -> None:
        """Save current chapter."""
        if not self.current_chapter:
            self._new_chapter()
            return
        
        filepath = os.path.join(self.base_path, "chapters", self.current_chapter)
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.statusBar().showMessage(f"Saved: {self.current_chapter}")
            logger.info(f"Saved chapter: {self.current_chapter}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save chapter:\n{e}")
            logger.error(f"Error saving chapter: {e}")
    
    def _new_chapter(self) -> None:
        """Create new chapter."""
        name, ok = QInputDialog.getText(self, "New Chapter", "Chapter name:")
        if ok and name:
            if not name.endswith(('.md', '.txt')):
                name += '.md'
            filepath = os.path.join(self.base_path, "chapters", name)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {name.replace('.md', '').replace('.txt', '')}\n\n")
            self._refresh_chapter_list()
            self.current_chapter = name
            self.editor.setPlainText(f"# {name.replace('.md', '').replace('.txt', '')}\n\n")
            self.statusBar().showMessage(f"Created: {name}")
            logger.info(f"Created new chapter: {name}")
    
    def _run_era_lint(self) -> None:
        """Lint current editor content for era violations."""
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Info", "No text to lint.")
            return
        
        if not self.era_linter:
            QMessageBox.warning(self, "Error", "Era linter not available.")
            return
        
        try:
            issues = self.era_linter.lint(text)
            summary = self.era_linter.get_summary(issues)
            
            report = f"Era Lint Report\n{'='*50}\n\n"
            report += f"Total Issues: {summary['total_issues']}\n"
            report += f"By Category: {summary['by_category']}\n"
            report += f"By Severity: {summary['by_severity']}\n\n"
            report += "Issues:\n" + "-"*50 + "\n"
            
            for issue in issues[:50]:  # Show first 50
                report += f"\nLine {issue['line']}: {issue['term']} ({issue['category']})\n"
                report += f"  Context: {issue['context'][:100]}\n"
                report += f"  Suggestion: {issue['suggestion']}\n"
            
            self.ai_output.setPlainText(report)
            self.statusBar().showMessage(f"Era lint complete: {summary['total_issues']} issues found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Era lint failed:\n{e}")
            logger.error(f"Era lint error: {e}")
    
    def _run_quick_advice(self) -> None:
        """Get quick advice on current content."""
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Info", "No text to analyze.")
            return
        
        if not self.advisor_mode:
            QMessageBox.warning(self, "Error", "Advisor mode not available.")
            return
        
        try:
            chapter_name = self.current_chapter or "Current"
            analysis = self.advisor_mode.analyze_chapter(text, chapter_name)
            
            output = f"Quick Advice for {chapter_name}\n{'='*50}\n\n"
            output += f"Summary: {analysis.get('summary', {}).get('total_issues', 0)} issues found\n\n"
            
            # Show top priorities
            revision_priority = analysis.get('revision_priority', {})
            if revision_priority:
                output += "Revision Priorities:\n"
                for priority in ['high_priority', 'medium_priority', 'low_priority']:
                    items = revision_priority.get(priority, [])
                    if items:
                        output += f"\n{priority.replace('_', ' ').title()}:\n"
                        for item in items[:5]:
                            output += f"  • {item}\n"
            
            self.ai_output.setPlainText(output)
            self.statusBar().showMessage("Quick advice generated")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Advisor analysis failed:\n{e}")
            logger.error(f"Advisor error: {e}")
    
    def _send_to_ai(self) -> None:
        """Send query to AI."""
        query = self.ai_input.text().strip()
        if not query:
            return
        
        if not self.model_router:
            QMessageBox.warning(self, "Error", "AI model router not available.")
            return
        
        self.ai_input.clear()
        self.ai_output.append(f"\n> {query}\n")
        
        # Get model
        model_map = {
            "Claude Sonnet": ModelType.CLAUDE_SONNET,
            "Claude Haiku": ModelType.CLAUDE_HAIKU,
            "GPT-4o": ModelType.GPT_4O,
            "Gemini Pro": ModelType.GEMINI_PRO
        }
        model = model_map.get(self.model_combo.currentText(), ModelType.CLAUDE_SONNET)
        
        # Include editor context
        context = self.editor.toPlainText()[:2000] if self.editor.toPlainText() else ""
        
        prompt = f"Context (current chapter excerpt):\n{context}\n\nUser question: {query}"
        
        try:
            response = self.model_router.generate(prompt, model)
            self.ai_output.append(response)
            self.statusBar().showMessage("AI response generated")
        except Exception as e:
            self.ai_output.append(f"Error: {str(e)}")
            logger.error(f"AI query error: {e}")
    
    def _enter_writing_mode(self) -> None:
        """Open Writing Mode checklist dialog."""
        current_chapter = None
        if self.current_chapter:
            current_chapter = self.current_chapter.replace('.txt', '').replace('.md', '')
        
        dialog = WritingModeDialog(
            self,
            canon_manager=self.canon_manager,
            current_chapter=current_chapter
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session_intent = dialog.get_session_intent()
            if session_intent:
                self.statusBar().showMessage(f"Writing Mode: {session_intent[:50]}...")
            else:
                self.statusBar().showMessage("Writing Mode: Active")
            logger.info("Writing Mode entered")
    
    # -----------------------------------------------------------
    # RESEARCH TAB METHODS
    # -----------------------------------------------------------
    
    def _refresh_research_list(self) -> None:
        """Refresh research document list."""
        self.research_list.clear()
        if not self.research_digestor:
            return
        
        try:
            docs = self.research_digestor.list_documents()
            for doc in docs:
                doc_id = doc.get('doc_id', 'unknown')
                title = doc.get('original_name', doc.get('title', 'Untitled'))
                status = doc.get('status', 'unknown')
                research_class = doc.get('classification', '-')
                
                item = QTreeWidgetItem([title, status, research_class])
                item.setData(0, Qt.ItemDataRole.UserRole, doc_id)
                self.research_list.addTopLevelItem(item)
        except Exception as e:
            logger.error(f"Error refreshing research list: {e}")
    
    def _on_research_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle research item selection."""
        self.selected_research_doc = item.data(0, Qt.ItemDataRole.UserRole)
    
    def _update_research_stats(self) -> None:
        """Update research statistics display."""
        if not self.research_digestor:
            self.research_stats.setText("Research digestor not available")
            return
        
        try:
            stats = self.research_digestor.get_stats()
            text = f"Total: {stats['total']}\n"
            text += f"Unprocessed: {stats['by_status'].get('unprocessed', 0)}\n"
            text += f"Classified: {stats['by_status'].get('classified', 0)}\n"
            text += f"Distilled: {stats['by_status'].get('distilled', 0)}\n"
            text += f"Promoted: {stats['by_status'].get('promoted', 0)}"
            self.research_stats.setText(text)
        except Exception as e:
            logger.error(f"Error updating research stats: {e}")
            self.research_stats.setText("Error loading stats")
    
    def _ingest_research(self) -> None:
        """Ingest new research document."""
        if not self.research_digestor:
            QMessageBox.warning(self, "Error", "Research digestor not available.")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Research Document", "",
            "Documents (*.txt *.md *.docx *.pdf);;All Files (*)"
        )
        if filepath:
            intent = self.intent_input.text().strip() or "Historical Context"
            try:
                doc = self.research_digestor.ingest(filepath, intent)
                self._refresh_research_list()
                self._update_research_stats()
                self.statusBar().showMessage(f"Ingested: {doc.get('original_name', 'document')}")
                QMessageBox.information(self, "Success", f"Document ingested: {doc.get('doc_id', 'unknown')}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to ingest document:\n{e}")
                logger.error(f"Ingest error: {e}")
    
    def _classify_research(self) -> None:
        """Classify selected research document."""
        if not hasattr(self, 'selected_research_doc') or not self.selected_research_doc:
            QMessageBox.warning(self, "Error", "Please select a document first.")
            return
        
        if not self.research_digestor:
            QMessageBox.warning(self, "Error", "Research digestor not available.")
            return
        
        try:
            research_class = ResearchClass(self.class_combo.currentText())
            doc = self.research_digestor.classify(self.selected_research_doc, research_class)
            self._refresh_research_list()
            self._update_research_stats()
            self.statusBar().showMessage(f"Classified: {doc.get('original_name', 'document')}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Classification failed:\n{e}")
            logger.error(f"Classification error: {e}")
    
    def _distill_research(self) -> None:
        """Distill selected research document."""
        if not hasattr(self, 'selected_research_doc') or not self.selected_research_doc:
            QMessageBox.warning(self, "Error", "Please select a document first.")
            return
        
        if not self.research_digestor:
            QMessageBox.warning(self, "Error", "Research digestor not available.")
            return
        
        try:
            result = self.research_digestor.distill(self.selected_research_doc)
            self._refresh_research_list()
            self._update_research_stats()
            self.statusBar().showMessage("Document distilled")
            QMessageBox.information(self, "Success", "Document distilled successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Distillation failed:\n{e}")
            logger.error(f"Distillation error: {e}")
    
    def _promote_research(self) -> None:
        """Promote selected research document."""
        if not hasattr(self, 'selected_research_doc') or not self.selected_research_doc:
            QMessageBox.warning(self, "Error", "Please select a document first.")
            return
        
        if not self.research_digestor:
            QMessageBox.warning(self, "Error", "Research digestor not available.")
            return
        
        try:
            research_class = ResearchClass(self.class_combo.currentText())
            doc = self.research_digestor.promote(self.selected_research_doc, research_class)
            self._refresh_research_list()
            self._update_research_stats()
            self.statusBar().showMessage("Document promoted")
            QMessageBox.information(self, "Success", f"Document promoted to {research_class.value}.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Promotion failed:\n{e}")
            logger.error(f"Promotion error: {e}")
    
    def _reject_research(self) -> None:
        """Reject selected research document."""
        if not hasattr(self, 'selected_research_doc') or not self.selected_research_doc:
            QMessageBox.warning(self, "Error", "Please select a document first.")
            return
        
        if not self.research_digestor:
            QMessageBox.warning(self, "Error", "Research digestor not available.")
            return
        
        reason, ok = QInputDialog.getText(self, "Reject Document", "Reason for rejection:")
        if ok and reason:
            try:
                doc = self.research_digestor.reject(self.selected_research_doc, reason)
                self._refresh_research_list()
                self._update_research_stats()
                self.statusBar().showMessage("Document rejected")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Rejection failed:\n{e}")
                logger.error(f"Rejection error: {e}")
    
    # -----------------------------------------------------------
    # CANON TAB METHODS
    # -----------------------------------------------------------
    
    def _refresh_canon_tree(self) -> None:
        """Refresh canon facts tree."""
        self.canon_tree.clear()
        if not self.canon_manager:
            return
        
        try:
            all_facts = self.canon_manager.get_all_facts()
            for fact_key, fact_data in all_facts.items():
                value = fact_data.get('value', '')
                source = fact_data.get('source_chapter', '')
                item = QTreeWidgetItem([fact_key, str(value)[:50], source])
                self.canon_tree.addTopLevelItem(item)
        except Exception as e:
            logger.error(f"Error refreshing canon tree: {e}")
    
    def _refresh_chapter_states(self) -> None:
        """Refresh chapter states list."""
        self.chapter_state_list.clear()
        if not self.canon_manager:
            return
        
        try:
            states = self.canon_manager.get_all_chapter_states()
            for chapter, state in states.items():
                item = QTreeWidgetItem([chapter, state.value])
                self.chapter_state_list.addTopLevelItem(item)
        except Exception as e:
            logger.error(f"Error refreshing chapter states: {e}")
    
    def _add_canon_fact(self) -> None:
        """Add new canon fact."""
        if not self.canon_manager:
            QMessageBox.warning(self, "Error", "Canon manager not available.")
            return
        
        fact_key, ok1 = QInputDialog.getText(self, "Add Canon Fact", "Fact Key:")
        if not ok1 or not fact_key:
            return
        
        fact_value, ok2 = QInputDialog.getText(self, "Add Canon Fact", "Fact Value:")
        if not ok2 or not fact_value:
            return
        
        source_chapter, ok3 = QInputDialog.getText(self, "Add Canon Fact", "Source Chapter:")
        if not ok3 or not source_chapter:
            return
        
        try:
            self.canon_manager.add_fact(fact_key, fact_value, source_chapter)
            self._refresh_canon_tree()
            self.statusBar().showMessage(f"Added canon fact: {fact_key}")
            QMessageBox.information(self, "Success", "Canon fact added.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add fact:\n{e}")
            logger.error(f"Add fact error: {e}")
    
    def _set_chapter_state(self, state: ChapterState) -> None:
        """Set chapter lock state."""
        if not self.canon_manager:
            QMessageBox.warning(self, "Error", "Canon manager not available.")
            return
        
        items = self.chapter_state_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Error", "Please select a chapter first.")
            return
        
        chapter_name = items[0].text(0)
        reason = None
        
        if state == ChapterState.CANON_LOCKED:
            reason, ok = QInputDialog.getText(self, "Lock Chapter", "Reason for locking:")
            if not ok or not reason:
                return
        
        try:
            self.canon_manager.set_chapter_state(chapter_name, state, reason)
            self._refresh_chapter_states()
            self.statusBar().showMessage(f"Set {chapter_name} to {state.value}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set chapter state:\n{e}")
            logger.error(f"Set chapter state error: {e}")
    
    def _run_regression_checks(self) -> None:
        """Run full regression check suite."""
        if not self.regression_checker:
            QMessageBox.warning(self, "Error", "Regression checker not available.")
            return
        
        try:
            results = self.regression_checker.run_all_checks()
            summary = results.get('summary', {})
            
            report = f"Regression Check Report\n{'='*60}\n\n"
            report += f"Total Issues: {summary.get('total_issues', 0)}\n"
            report += f"High Severity: {summary.get('high_severity', 0)}\n"
            report += f"Medium Severity: {summary.get('medium_severity', 0)}\n"
            report += f"Low Severity: {summary.get('low_severity', 0)}\n\n"
            
            for check_type, issues in results.items():
                if check_type != 'summary' and isinstance(issues, list):
                    if issues:
                        report += f"\n{check_type.replace('_', ' ').title()}:\n"
                        for issue in issues[:10]:  # Show first 10
                            report += f"  • {issue.get('type', 'unknown')}: {issue.get('chapter', 'unknown')}\n"
            
            self.regression_output.setPlainText(report)
            self.statusBar().showMessage("Regression checks complete")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Regression check failed:\n{e}")
            logger.error(f"Regression check error: {e}")
    
    # -----------------------------------------------------------
    # ADVISOR TAB METHODS
    # -----------------------------------------------------------
    
    def _refresh_advisor_chapters(self) -> None:
        """Refresh advisor chapter list."""
        self.advisor_chapter_combo.clear()
        chapters_dir = os.path.join(self.base_path, "chapters")
        if os.path.exists(chapters_dir):
            for f in sorted(os.listdir(chapters_dir)):
                if f.endswith(('.md', '.txt')):
                    self.advisor_chapter_combo.addItem(f)
    
    def _run_advisor_analysis(self) -> None:
        """Run full advisor analysis on selected chapter."""
        chapter_name = self.advisor_chapter_combo.currentText()
        if not chapter_name:
            QMessageBox.warning(self, "Error", "Please select a chapter.")
            return
        
        if not self.advisor_mode:
            QMessageBox.warning(self, "Error", "Advisor mode not available.")
            return
        
        filepath = os.path.join(self.base_path, "chapters", chapter_name)
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "Error", "Chapter file not found.")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Run era lint
            if self.era_linter:
                issues = self.era_linter.lint(content)
                summary = self.era_linter.get_summary(issues)
                era_text = f"Era Language Issues\n{'='*50}\n\n"
                era_text += f"Total: {summary['total_issues']}\n"
                era_text += f"By Category: {summary['by_category']}\n\n"
                for issue in issues[:20]:
                    era_text += f"Line {issue['line']}: {issue['term']} ({issue['category']})\n"
                    era_text += f"  → {issue['suggestion']}\n\n"
                self.era_lint_output.setPlainText(era_text)
            
            # Run advisor analysis
            analysis = self.advisor_mode.analyze_chapter(content, chapter_name)
            
            # Recommendations
            rec_text = f"Advisor Analysis: {chapter_name}\n{'='*50}\n\n"
            summary = analysis.get('summary', {})
            rec_text += f"Total Issues: {summary.get('total_issues', 0)}\n\n"
            
            revision_priority = analysis.get('revision_priority', {})
            if revision_priority:
                rec_text += "Revision Priorities:\n"
                for priority in ['high_priority', 'medium_priority']:
                    items = revision_priority.get(priority, [])
                    if items:
                        rec_text += f"\n{priority.replace('_', ' ').title()}:\n"
                        for item in items[:5]:
                            rec_text += f"  • {item}\n"
            
            self.rec_output.setPlainText(rec_text)
            self.statusBar().showMessage(f"Analyzed: {chapter_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Advisor analysis failed:\n{e}")
            logger.error(f"Advisor analysis error: {e}")
    
    # -----------------------------------------------------------
    # EXPORT TAB METHODS
    # -----------------------------------------------------------
    
    def _get_all_chapters(self) -> List[Dict[str, str]]:
        """Load all chapters for export."""
        chapters = []
        chapters_dir = os.path.join(self.base_path, "chapters")
        if os.path.exists(chapters_dir):
            for f in sorted(os.listdir(chapters_dir)):
                if f.endswith(('.md', '.txt')):
                    filepath = os.path.join(chapters_dir, f)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            chapters.append({
                                'name': f.replace('.md', '').replace('.txt', ''),
                                'text': file.read()
                            })
                    except Exception as e:
                        logger.warning(f"Error loading chapter {f}: {e}")
        return chapters
    
    def _export_docx(self) -> None:
        """Export manuscript as DOCX."""
        if not self.docx_exporter:
            QMessageBox.warning(self, "Error", "python-docx not installed. Install with: pip install python-docx")
            return
        
        chapters = self._get_all_chapters()
        if not chapters:
            QMessageBox.warning(self, "Error", "No chapters to export")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save DOCX", f"{self.export_title.text() or 'manuscript'}.docx",
            "Word Document (*.docx)"
        )
        
        if filepath:
            try:
                title = self.export_title.text() or "Manuscript"
                author = self.export_author.text() or "Author"
                
                # Convert chapters to format expected by exporter
                chapter_list = [{'name': ch['name'], 'text': ch['text']} for ch in chapters]
                self.docx_exporter.export_full_manuscript(chapter_list, filepath, title, author)
                self.export_status.append(f"✅ Exported DOCX: {filepath}")
                self.statusBar().showMessage("DOCX exported successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Export failed:\n{e}")
                logger.error(f"DOCX export error: {e}")
    
    def _export_epub(self) -> None:
        """Export manuscript as EPUB."""
        if not self.epub_exporter:
            QMessageBox.warning(self, "Error", "ebooklib not installed. Install with: pip install ebooklib")
            return
        
        chapters = self._get_all_chapters()
        if not chapters:
            QMessageBox.warning(self, "Error", "No chapters to export")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save EPUB", f"{self.export_title.text() or 'manuscript'}.epub",
            "EPUB (*.epub)"
        )
        
        if filepath:
            try:
                title = self.export_title.text() or "Manuscript"
                author = self.export_author.text() or "Author"
                
                # Convert chapters to format expected by exporter
                chapter_list = [{'name': ch['name'], 'text': ch['text']} for ch in chapters]
                self.epub_exporter.export_full_manuscript(chapter_list, filepath, title, author)
                self.export_status.append(f"✅ Exported EPUB: {filepath}")
                self.statusBar().showMessage("EPUB exported successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Export failed:\n{e}")
                logger.error(f"EPUB export error: {e}")
    
    def _build_query_package(self) -> None:
        """Build query package for agent submission."""
        if not self.query_builder:
            QMessageBox.warning(self, "Error", "Query builder not available.")
            return
        
        chapters = self._get_all_chapters()
        if not chapters:
            QMessageBox.warning(self, "Error", "No chapters to export")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        
        if output_dir:
            try:
                # Convert chapters to format expected by query builder
                chapter_list = [{'name': ch['name'], 'text': ch['text']} for ch in chapters]
                package = self.query_builder.build_package(
                    chapter_list,
                    output_dir,
                    query_letter=None,
                    include_references=True,
                    include_canon=True
                )
                self.export_status.append(f"✅ Query package built in: {output_dir}")
                for name, path in package.items():
                    self.export_status.append(f"   - {name}: {path}")
                self.statusBar().showMessage("Query package built successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Query package build failed:\n{e}")
                logger.error(f"Query package error: {e}")
    
    # -----------------------------------------------------------
    # MENU AND STATUS BAR
    # -----------------------------------------------------------
    
    def _init_menu(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Chapter", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._new_chapter)
        file_menu.addAction(new_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._save_chapter)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        lint_action = QAction("&Era Lint Current", self)
        lint_action.setShortcut(QKeySequence("Ctrl+L"))
        lint_action.triggered.connect(self._run_era_lint)
        tools_menu.addAction(lint_action)
        
        regression_action = QAction("&Run Regression Checks", self)
        regression_action.triggered.connect(self._run_regression_checks)
        tools_menu.addAction(regression_action)
        
        writing_mode_action = QAction("Enter &Writing Mode...", self)
        writing_mode_action.setShortcut(QKeySequence("Ctrl+W"))
        writing_mode_action.triggered.connect(self._enter_writing_mode)
        tools_menu.addAction(writing_mode_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _init_statusbar(self) -> None:
        """Create status bar."""
        self.statusBar().showMessage("Ready")
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self, "About Novel Assistant",
            "Novel Assistant v3\n\n"
            "A comprehensive writing tool for historical fiction.\n\n"
            "Features:\n"
            "• Multi-model AI support\n"
            "• Research governance\n"
            "• Canon management\n"
            "• Era-appropriate language linting\n"
            "• Export to DOCX/EPUB\n"
            "• Query package builder"
        )


# -----------------------------------------------------------
# MAIN ENTRY POINT
# -----------------------------------------------------------

def run_gui():
    """Run the GUI application."""
    app = QApplication([])
    app.setStyle('Fusion')
    
    window = NovelAssistantApp()
    window.show()
    
    app.exec()


if __name__ == "__main__":
    run_gui()

